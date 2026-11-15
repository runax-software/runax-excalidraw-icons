"""Icons as native Excalidraw shapes instead of images.

A library of image items can't be published on libraries.excalidraw.com: its library format has
no place for image data. Converting each SVG into Excalidraw's own elements makes the icon part
of the library itself, editable and recolorable like anything else drawn.

The conversion is an approximation of the SVG, with known limits:
- curves become polylines (CURVE_SAMPLES points per segment);
- Excalidraw shapes can't have cut-outs, so each hole is joined to its outline by a zero-width
  slit ("keyhole"): one outline that goes around the hole, which fills the same way;
- Excalidraw has no gradients, so a gradient becomes the average of its colors.
Only use it for icons whose terms allow changing them (not Azure's or AWS's).
"""

import io
import re
from dataclasses import dataclass

from svgelements import SVG, Close, Color, Line, Move, Path as SvgPath, Shape

from ..icon import Icon
from .elements import ICON_SIZE, LABEL_GAP, Element, ElementFactory, LineElement, wrap_label
from .geometry import Point

CURVE_SAMPLES = 8  # points per curved segment
MIN_STROKE = 0.5  # Excalidraw's thinnest visible line

GRADIENT_RE = re.compile(
    r"<(?:linear|radial)Gradient\b([^>]*?)(?:/>|>(.*?)</(?:linear|radial)Gradient>)", re.S | re.I
)
ID_RE = re.compile(r'\bid="([^"]+)"')
HREF_RE = re.compile(r'\b(?:xlink:)?href="#([^"]+)"')
STOP_COLOR_RE = re.compile(r'stop-color\s*[:=]\s*"?\s*(#[0-9a-fA-F]{3,8}|[a-zA-Z]+)')
URL_RE = re.compile(r"url\(\s*#([^)]+)\)")


@dataclass(frozen=True)
class Part:
    """One outline of the SVG (holes already joined in), in pixels, with how it's painted."""

    points: list[Point]
    closed: bool
    fill: str | None
    stroke: str | None
    stroke_width: float


class NativeConverter:
    """Converts an icon's SVG into Excalidraw line elements fitted in a box."""

    def __init__(self, factory: ElementFactory):
        self.factory = factory

    def icon(self, icon: Icon, label: str, x: float = 0, y: float = 0, box: int = ICON_SIZE) -> list[Element]:
        """The icon's shapes with its caption below, grouped: a native library item."""
        group_id = self.factory.new_id()
        shapes = self.shapes(icon, Point(x, y), box, group_id)
        caption = self.factory.text(wrap_label(label), x + box / 2, y + box + LABEL_GAP, group_id=group_id)
        return [*shapes, caption]

    def shapes(self, icon: Icon, at: Point, box: int, group_id: str) -> list[LineElement]:
        # Parse the rendered document: it has an absolute size (a `1em` or unitless SVG would
        # not), and svgelements reifies everything into that pixel space.
        document = icon.document.rendered()
        svg = SVG.parse(io.BytesIO(document.data), reify=True)
        if svg.width is None or svg.height is None:
            raise ValueError(f"{icon.path}: SVG without a size")
        width, height = float(svg.width), float(svg.height)
        scale = box / max(width, height)
        offset = Point(at.x + (box - width * scale) / 2, at.y + (box - height * scale) / 2)
        gradients = _gradient_colors(document.text)

        # Document order is paint order, as in SVG.
        return [
            self.factory.line(
                [Point(offset.x + px.x * scale, offset.y + px.y * scale) for px in part.points],
                group_id,
                part.closed,
                part.fill,
                part.stroke,
                max(part.stroke_width * scale, MIN_STROKE),
            )
            for part in self._parts(svg, gradients)
        ]

    def _parts(self, svg: SVG, gradients: dict[str, str]) -> list[Part]:
        parts: list[Part] = []
        for element in svg.elements():
            if not isinstance(element, Shape) or isinstance(element, SVG):
                continue

            fill = _paint(element, "fill", gradients)
            stroke = _paint(element, "stroke", gradients)
            if not fill and not stroke:
                continue
            stroke_width = float(element.implicit_stroke_width or 0) if stroke else 0.0

            subpaths = _subpaths(SvgPath(element))
            if fill:
                outlines = _join_holes([points for points, _ in subpaths])
                parts += [Part(points, True, fill, stroke, stroke_width) for points in outlines]
            else:
                parts += [Part(points, closed, None, stroke, stroke_width) for points, closed in subpaths]
        return parts


def _paint(element: Shape, attribute: str, gradients: dict[str, str]) -> str | None:
    """A shape's fill or stroke as a hex color; a gradient's first color; None if unpainted."""
    raw = str((element.values or {}).get(attribute, ""))
    url = URL_RE.search(raw)
    if url:
        return gradients.get(url.group(1))

    color = getattr(element, attribute)
    if color is None or color.value is None or Color(color).alpha == 0:
        return None
    return Color(color).hexrgb


def _gradient_colors(text: str) -> dict[str, str]:
    """Gradient id -> the average of its stop colors, following href chains (Inkscape splits gradients
    into a stops-only one and positioned ones that reference it)."""
    stops: dict[str, str] = {}
    refs: dict[str, str] = {}
    for attrs, body in GRADIENT_RE.findall(text):
        gradient_id = ID_RE.search(attrs)
        if not gradient_id:
            continue
        colors = [Color(m) for m in STOP_COLOR_RE.findall(body or "")]
        colors = [c for c in colors if c.value is not None]
        if colors:
            stops[gradient_id.group(1)] = _average(colors)
        href = HREF_RE.search(attrs)
        if href:
            refs[gradient_id.group(1)] = href.group(1)

    colors = dict(stops)
    for gradient_id in refs:
        seen, current = set(), gradient_id
        while current not in stops and current in refs and current not in seen:
            seen.add(current)
            current = refs[current]
        if current in stops:
            colors[gradient_id] = stops[current]
    return colors


def _subpaths(path: SvgPath) -> list[tuple[list[Point], bool]]:
    """Each subpath as a polyline, and whether it's closed."""
    result: list[tuple[list[Point], bool]] = []
    points: list[Point] = []
    closed = False
    for segment in path.segments():
        if isinstance(segment, Move):
            if len(points) > 1:
                result.append((points, closed))
            points, closed = [_point(segment.end)], False
        elif isinstance(segment, Close):
            closed = True
        elif isinstance(segment, Line):
            points.append(_point(segment.end))
        else:
            for i in range(1, CURVE_SAMPLES + 1):
                points.append(_point(segment.point(i / CURVE_SAMPLES)))
    if len(points) > 1:
        result.append((points, closed))
    return result


def _inside(point: Point, polygon: list[Point]) -> bool:
    """Ray casting: whether `point` is inside `polygon`."""
    hit = False
    for a, b in zip(polygon, polygon[1:] + polygon[:1]):
        if (a.y > point.y) != (b.y > point.y) and point.x < (b.x - a.x) * (point.y - a.y) / (b.y - a.y) + a.x:
            hit = not hit
    return hit


def _point(p) -> Point:
    """An svgelements point as ours (svgelements types its coordinates as optional)."""
    if p is None or p.x is None or p.y is None:
        raise ValueError("path segment without a point")
    return Point(float(p.x), float(p.y))


def _join_holes(rings: list[list[Point]]) -> list[list[Point]]:
    """Filled subpaths as outlines without holes. By even-odd nesting, a ring inside an odd
    number of others is a hole of the smallest ring around it; each hole is spliced into that
    ring through its two closest points, running the other way, so the joined outline fills
    everything except the hole whatever fill rule draws it."""
    depth = [sum(_inside(ring[0], other) for other in rings if other is not ring) for ring in rings]
    outers = {i: list(ring) for i, ring in enumerate(rings) if depth[i] % 2 == 0}

    for i, ring in enumerate(rings):
        if depth[i] % 2 == 0:
            continue
        containers = [o for o in outers if depth[o] == depth[i] - 1 and _inside(ring[0], rings[o])]
        if not containers:
            outers[i] = list(ring)  # an unmatched hole: draw it rather than lose it
            continue
        outer = outers[containers[0]]
        hole = ring if _clockwise(ring) != _clockwise(outer) else ring[::-1]
        a, b = min(
            ((a, b) for a in range(len(outer)) for b in range(len(hole))),
            key=lambda ab: (outer[ab[0]].x - hole[ab[1]].x) ** 2 + (outer[ab[0]].y - hole[ab[1]].y) ** 2,
        )
        outers[containers[0]] = outer[: a + 1] + hole[b:] + hole[: b + 1] + outer[a:]

    return [outers[i] for i in sorted(outers)]


def _clockwise(ring: list[Point]) -> bool:
    return sum((b.x - a.x) * (b.y + a.y) for a, b in zip(ring, ring[1:] + ring[:1])) > 0


def _average(colors: list[Color]) -> str:
    red, green, blue = (round(sum(getattr(c, channel) for c in colors) / len(colors)) for channel in ("red", "green", "blue"))
    return f"#{red:02x}{green:02x}{blue:02x}"
