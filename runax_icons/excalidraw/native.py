"""Icons as native Excalidraw shapes instead of images.

Excalidraw drops a library's images on import (its library format has no place for image
data), so image items show as empty boxes in the library panel. Converting each SVG into
Excalidraw's own elements makes the icon part of the library itself.

The conversion is an approximation of the SVG, with known limits:
- curves become polylines (CURVE_SAMPLES points per segment);
- Excalidraw shapes can't have cut-outs, so each hole is joined to its outline by a zero-width
  slit ("keyhole"): one outline that goes around the hole, which fills the same way;
- Excalidraw has no gradients, so a gradient becomes the average of its colors and opacities;
- shapes outside the viewBox are dropped, and filled ones crossing it are clipped to it;
- text keeps its position, size and color, in Excalidraw's font;
- stylesheet selectors only match by their last part (`.svglite rect` as `rect`).
"""

import io
import re
from dataclasses import dataclass

from svgelements import SVG, Close, Color, Line, Matrix, Move, Path as SvgPath, Shape, Text

from ..icon import Icon
from .elements import ICON_SIZE, LABEL_GAP, Element, ElementFactory, wrap_label
from .geometry import Point

CURVE_SAMPLES = 8  # points per curved segment
MIN_STROKE = 0.5  # Excalidraw's thinnest visible line
EDGE = 0.5  # pixels a point may stray outside the viewBox and still count as inside
BASELINE = 0.9  # an Excalidraw text's baseline, in font sizes below its top
ALIGN = {"start": "left", "middle": "center", "end": "right"}

GRADIENT_RE = re.compile(
    r"<(?:linear|radial)Gradient\b([^>]*?)(?:/>|>(.*?)</(?:linear|radial)Gradient>)", re.S | re.I
)
ID_RE = re.compile(r'\bid="([^"]+)"')
HREF_RE = re.compile(r'\b(?:xlink:)?href="#([^"]+)"')
STOP_RE = re.compile(r"<stop\b[^>]*>", re.I)
STOP_COLOR_RE = re.compile(r'stop-color\s*[:=]\s*"?\s*(#[0-9a-fA-F]{3,8}|[a-zA-Z]+)')
STOP_OPACITY_RE = re.compile(r'stop-opacity\s*[:=]\s*"?\s*([\d.]+)')
URL_RE = re.compile(r"url\(\s*#([^)]+)\)")
STYLE_RE = re.compile(r"(<style\b[^>]*>)(.*?)(</style>)", re.S | re.I)
CSS_RULE_RE = re.compile(r"([^{}]+)(\{[^}]*\})")
CDATA_RE = re.compile(r"^(\s*<!\[CDATA\[)(.*)(\]\]>\s*)$", re.S)


@dataclass(frozen=True)
class Paint:
    color: str
    alpha: float  # 0 to 1


@dataclass(frozen=True)
class Part:
    """One outline of the SVG (holes already joined in), in pixels, with how it's painted."""

    points: list[Point]
    closed: bool
    fill: str | None
    stroke: str | None
    stroke_width: float
    opacity: float  # 0 to 1


@dataclass(frozen=True)
class Glyphs:
    """An SVG text, in pixels: its baseline anchor and how it's aligned there."""

    text: str
    anchor: Point
    size: float
    align: str
    fill: str
    opacity: float


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

    def shapes(self, icon: Icon, at: Point, box: int, group_id: str) -> list[Element]:
        # Parse the rendered document: it has an absolute size (a `1em` or unitless SVG would
        # not), and svgelements reifies everything into that pixel space.
        document = icon.document.rendered()
        svg = SVG.parse(io.BytesIO(_simple_css(document.text).encode()), reify=True)
        if svg.width is None or svg.height is None:
            raise ValueError(f"{icon.path}: SVG without a size")
        width, height = float(svg.width), float(svg.height)
        scale = box / max(width, height)
        offset = Point(at.x + (box - width * scale) / 2, at.y + (box - height * scale) / 2)
        gradients = _gradient_colors(document.text)

        def place(p: Point) -> Point:
            return Point(offset.x + p.x * scale, offset.y + p.y * scale)

        # Document order is paint order, as in SVG.
        elements: list[Element] = []
        for part in self._parts(svg, gradients):
            if isinstance(part, Glyphs):
                size = part.size * scale
                anchor = place(part.anchor)
                elements.append(
                    self.factory.text(
                        part.text, anchor.x, anchor.y - size * BASELINE, group_id,
                        font_size=round(size, 2), color=part.fill, align=part.align,
                    )
                )
                elements[-1].opacity = round(part.opacity * 100)
                continue
            clipped = _clip(part, width, height)
            if clipped is None:
                continue
            elements.append(
                self.factory.line(
                    [place(p) for p in clipped.points],
                    group_id,
                    clipped.closed,
                    clipped.fill,
                    clipped.stroke,
                    max(clipped.stroke_width * scale, MIN_STROKE),
                    round(clipped.opacity * 100),
                )
            )
        return elements

    def _parts(self, svg: SVG, gradients: dict[str, Paint]) -> list[Part | Glyphs]:
        parts: list[Part | Glyphs] = []
        for element in svg.elements():
            if isinstance(element, Text):
                glyphs = _glyphs(element, gradients)
                if glyphs:
                    parts.append(glyphs)
                continue
            if not isinstance(element, Shape) or isinstance(element, SVG):
                continue

            opacity = float((element.values or {}).get("opacity", 1) or 1)
            fill = _paint(element, "fill", gradients)
            stroke = _paint(element, "stroke", gradients)
            if not fill and not stroke:
                continue
            stroke_width = float(element.implicit_stroke_width or 0) if stroke else 0.0
            # One element has one opacity: the fill's when filled, else the stroke's.
            alpha = opacity * (fill or stroke).alpha  # type: ignore[union-attr]
            if round(alpha * 100) == 0:
                continue
            fill_color = fill.color if fill else None
            stroke_color = stroke.color if stroke else None

            subpaths = _subpaths(SvgPath(element))
            if fill:
                outlines = _join_holes([points for points, _ in subpaths])
                parts += [Part(points, True, fill_color, stroke_color, stroke_width, alpha) for points in outlines]
            else:
                parts += [Part(points, closed, None, stroke_color, stroke_width, alpha) for points, closed in subpaths]
        return parts


def _glyphs(element: Text, gradients: dict[str, Paint]) -> Glyphs | None:
    """A text element in pixels, or None if it has no text of its own (only <tspan>s, which
    come as their own elements) or no paint."""
    if not (element.text or "").strip():
        return None
    fill = _paint(element, "fill", gradients)
    opacity = float((element.values or {}).get("opacity", 1) or 1) * (fill.alpha if fill else 0)
    if not fill or round(opacity * 100) == 0:
        return None
    matrix = element.transform or Matrix()
    anchor = _point(matrix.point_in_matrix_space((float(element.x or 0), float(element.y or 0))))
    size = float(str(element.font_size or 16)) * abs(matrix.a * matrix.d - matrix.b * matrix.c) ** 0.5
    align = ALIGN.get(str(element.anchor or "start"), "left")
    return Glyphs(element.text.strip(), anchor, size, align, fill.color, opacity)


def _paint(element: Shape | Text, attribute: str, gradients: dict[str, Paint]) -> Paint | None:
    """A shape's fill or stroke as a hex color and its alpha (a gradient's average); None if
    unpainted."""
    raw = str((element.values or {}).get(attribute, ""))
    url = URL_RE.search(raw)
    if url:
        return gradients.get(url.group(1))

    color = getattr(element, attribute)
    if color is None or color.value is None or not Color(color).alpha:
        return None
    return Paint(str(Color(color).hexrgb), (Color(color).alpha or 0) / 255)


def _simple_css(text: str) -> str:
    """Stylesheets with each selector cut to its last part: svgelements matches `rect` or
    `.cls-1` but not `.svglite rect`, and leaves those shapes painted black."""

    def rules(css: str) -> str:
        def rule(match: re.Match) -> str:
            selectors = [re.split(r"[\s>+~]+", s.strip())[-1] for s in match.group(1).split(",")]
            return ", ".join(selectors) + " " + match.group(2)

        return CSS_RULE_RE.sub(rule, css)

    def style(match: re.Match) -> str:
        cdata = CDATA_RE.match(match.group(2))
        body = cdata.group(1) + rules(cdata.group(2)) + cdata.group(3) if cdata else rules(match.group(2))
        return match.group(1) + body + match.group(3)

    return STYLE_RE.sub(style, text)


def _clip(part: Part, width: float, height: float) -> Part | None:
    """The part as seen through the viewBox (0, 0, width, height): whole when inside; dropped
    when outside (Illustrator artboard leftovers, wordmarks a crop removed), unless it's a
    filled shape around the whole view (a background); filled shapes crossing an edge cut to it,
    without their stroke, which would trace the cut."""
    inside = [-EDGE <= p.x <= width + EDGE and -EDGE <= p.y <= height + EDGE for p in part.points]
    if all(inside):
        return part
    if not part.fill:
        return part if any(inside) else None
    if not any(inside) and not _inside(Point(width / 2, height / 2), part.points):
        return None
    points = _clip_polygon(part.points, width, height)
    if len(points) < 3:
        return None
    return Part(points, True, part.fill, None, 0.0, part.opacity)


def _clip_polygon(points: list[Point], width: float, height: float) -> list[Point]:
    """Sutherland-Hodgman: the polygon cut to the rectangle (0, 0, width, height)."""
    edges = [
        (lambda p: p.x >= 0, lambda a, b: a.x / (a.x - b.x)),
        (lambda p: p.x <= width, lambda a, b: (a.x - width) / (a.x - b.x)),
        (lambda p: p.y >= 0, lambda a, b: a.y / (a.y - b.y)),
        (lambda p: p.y <= height, lambda a, b: (a.y - height) / (a.y - b.y)),
    ]
    for keeps, crossing in edges:
        result: list[Point] = []
        for a, b in zip(points[-1:] + points[:-1], points):
            if keeps(b):
                if not keeps(a):
                    result.append(_lerp(a, b, crossing(a, b)))
                result.append(b)
            elif keeps(a):
                result.append(_lerp(a, b, crossing(a, b)))
        points = result
        if not points:
            break
    return points


def _lerp(a: Point, b: Point, t: float) -> Point:
    return Point(a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t)


def _gradient_colors(text: str) -> dict[str, Paint]:
    """Gradient id -> the average of its stop colors and opacities, following href chains
    (Inkscape splits gradients into a stops-only one and positioned ones that reference it)."""
    stops: dict[str, Paint] = {}
    refs: dict[str, str] = {}
    for attrs, body in GRADIENT_RE.findall(text):
        gradient_id = ID_RE.search(attrs)
        if not gradient_id:
            continue
        colors: list[Color] = []
        alphas: list[float] = []
        for stop in STOP_RE.findall(body or ""):
            color = STOP_COLOR_RE.search(stop)
            if not color or Color(color.group(1)).value is None:
                continue
            opacity = STOP_OPACITY_RE.search(stop)
            colors.append(Color(color.group(1)))
            alphas.append(float(opacity.group(1)) if opacity else 1.0)
        if colors:
            stops[gradient_id.group(1)] = Paint(_average(colors), sum(alphas) / len(alphas))
        href = HREF_RE.search(attrs)
        if href:
            refs[gradient_id.group(1)] = href.group(1)

    paints = dict(stops)
    for gradient_id in refs:
        seen, current = set(), gradient_id
        while current not in stops and current in refs and current not in seen:
            seen.add(current)
            current = refs[current]
        if current in stops:
            paints[gradient_id] = stops[current]
    return paints


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
