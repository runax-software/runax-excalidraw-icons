"""Excalidraw elements as typed objects, built by an ElementFactory and serialized with to_dict()."""

import uuid
from dataclasses import dataclass, field
from typing import Any

from ..icon import Icon
from .geometry import Point

ICON_SIZE = 64
LABEL_GAP = 8  # between an icon and its caption
FONT_SIZE = 14
LINE_HEIGHT = 1.25
FONT_FAMILY = 2  # Helvetica
CHAR_WIDTH = FONT_SIZE * 0.55  # average Helvetica glyph width estimate
MAX_LINE_CHARS = 18  # longer labels wrap onto a second line, Miro-style
VENDOR_WORDS = {"AWS", "Amazon", "Azure", "Microsoft", "Google"}
TEXT_COLOR = "#1e1e1e"


@dataclass
class Element:
    """The fields every Excalidraw element has. Subclasses add their own in `_fields()`."""

    type: str
    id: str
    x: float
    y: float
    width: float
    height: float
    seed: int
    version_nonce: int
    updated: int
    group_ids: list[str] = field(default_factory=list)
    stroke_color: str = "transparent"
    background_color: str = "transparent"
    stroke_width: float = 1
    stroke_style: str = "solid"
    roundness: dict | None = None
    bound_elements: list[dict] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "angle": 0,
            "strokeColor": self.stroke_color,
            "backgroundColor": self.background_color,
            "fillStyle": "solid",
            "strokeWidth": self.stroke_width,
            "strokeStyle": self.stroke_style,
            "roughness": 0,
            "opacity": 100,
            "groupIds": self.group_ids,
            "frameId": None,
            "roundness": self.roundness,
            "seed": self.seed,
            "version": 1,
            "versionNonce": self.version_nonce,
            "isDeleted": False,
            "boundElements": self.bound_elements,
            "updated": self.updated,
            "link": None,
            "locked": False,
            **self._fields(),
        }

    def _fields(self) -> dict[str, Any]:
        return {}


@dataclass
class ImageElement(Element):
    file_id: str = ""

    def _fields(self) -> dict[str, Any]:
        return {"status": "saved", "fileId": self.file_id, "scale": [1, 1], "crop": None}


@dataclass
class TextElement(Element):
    text: str = ""
    container_id: str | None = None

    def _fields(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "originalText": self.text,
            "fontSize": FONT_SIZE,
            "fontFamily": FONT_FAMILY,
            "textAlign": "center",
            "verticalAlign": "middle" if self.container_id else "top",
            "containerId": self.container_id,
            "autoResize": True,
            "lineHeight": LINE_HEIGHT,
            "baseline": round(FONT_SIZE * 0.88),
        }


@dataclass
class ArrowElement(Element):
    points: list[list[float]] = field(default_factory=list)
    start_binding: dict | None = None
    end_binding: dict | None = None

    def _fields(self) -> dict[str, Any]:
        return {
            "points": self.points,
            "lastCommittedPoint": None,
            "startBinding": self.start_binding,
            "endBinding": self.end_binding,
            "startArrowhead": None,
            "endArrowhead": "arrow",
            "elbowed": False,
        }


@dataclass
class LineElement(Element):
    """A polyline; closed (`polygon`) it's a shape filled with its background color."""

    points: list[list[float]] = field(default_factory=list)
    polygon: bool = False

    def _fields(self) -> dict[str, Any]:
        return {
            "points": self.points,
            "lastCommittedPoint": None,
            "startBinding": None,
            "endBinding": None,
            "startArrowhead": None,
            "endArrowhead": None,
            "polygon": self.polygon,
        }


class ElementFactory:
    """Creates elements with fresh ids and seeds, stamped with one time (`now`, unix ms)."""

    def __init__(self, now: int):
        self.now = now

    @staticmethod
    def new_id() -> str:
        return uuid.uuid4().hex[:20]

    @staticmethod
    def seed() -> int:
        return uuid.uuid4().int & 0x7FFFFFFF

    def _base(self, x: float, y: float, width: float, height: float, group_id: str | None) -> dict:
        return {
            "id": self.new_id(),
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "seed": self.seed(),
            "version_nonce": self.seed(),
            "updated": self.now,
            "group_ids": [group_id] if group_id else [],
        }

    def icon(
        self, icon: Icon, label: str, x: float = 0, y: float = 0, box: int = ICON_SIZE
    ) -> list[Element]:
        """An icon fitted in a `box`-pixel square, with its label below, grouped: the unit of
        every library item."""
        group_id = self.new_id()

        # Excalidraw stretches images to their element, so fit non-square icons in the box.
        width = round(box * min(1, icon.aspect), 2)
        height = round(box * min(1, 1 / icon.aspect), 2)
        image = ImageElement(
            type="image",
            file_id=icon.file_id,
            **self._base(x + (box - width) / 2, y + (box - height) / 2, width, height, group_id),
        )
        caption = self.text(wrap_label(label), x + box / 2, y + box + LABEL_GAP, group_id=group_id)
        return [image, caption]

    def text(
        self,
        text: str,
        center_x: float,
        top: float,
        group_id: str | None = None,
        container_id: str | None = None,
    ) -> TextElement:
        """A centered text element; `center_x` is its horizontal middle."""
        lines = text.split("\n")
        width = round(max(len(line) for line in lines) * CHAR_WIDTH, 2)
        height = round(len(lines) * FONT_SIZE * LINE_HEIGHT, 2)

        return TextElement(
            type="text",
            text=text,
            container_id=container_id,
            stroke_color=TEXT_COLOR,
            **self._base(center_x - width / 2, top, width, height, group_id),
        )

    def arrow(
        self, start: Point, end: Point, start_id: str | None, end_id: str | None, gap: float, **style: Any
    ) -> ArrowElement:
        """A straight arrow from `start` to `end`, bound to the elements at both ends (an end
        without an id stays free)."""
        return ArrowElement(
            type="arrow",
            points=[[0, 0], [end.x - start.x, end.y - start.y]],
            start_binding={"elementId": start_id, "focus": 0, "gap": gap} if start_id else None,
            end_binding={"elementId": end_id, "focus": 0, "gap": gap} if end_id else None,
            roundness={"type": 2},
            **style,
            **self._base(start.x, start.y, abs(end.x - start.x), abs(end.y - start.y), None),
        )

    def line(
        self,
        points: list[Point],
        group_id: str,
        closed: bool,
        fill: str | None,
        stroke: str | None,
        stroke_width: float,
    ) -> LineElement:
        """A shape traced through `points` (absolute): filled with `fill` when `closed`,
        outlined with `stroke`."""
        points = [Point(round(p.x, 2), round(p.y, 2)) for p in points]  # sub-pixel is noise
        if closed and points[0] != points[-1]:
            points = [*points, points[0]]

        start = points[0]
        xs, ys = [p.x for p in points], [p.y for p in points]
        return LineElement(
            type="line",
            points=[[round(p.x - start.x, 2), round(p.y - start.y, 2)] for p in points],
            polygon=closed,
            stroke_color=stroke or "transparent",
            background_color=fill if closed and fill else "transparent",
            stroke_width=stroke_width,
            **self._base(start.x, start.y, max(xs) - min(xs), max(ys) - min(ys), group_id),
        )

    def file(self, icon: Icon) -> dict[str, Any]:
        """The `files` entry holding an icon's SVG, keyed by its fileId."""
        return {
            "mimeType": "image/svg+xml",
            "id": icon.file_id,
            "dataURL": icon.data_url,
            "created": self.now,
            "lastRetrieved": self.now,
        }


def wrap_label(label: str) -> str:
    """One line if it fits in MAX_LINE_CHARS, else two lines as even as possible, never more
    (vendor guidelines: names fit on two lines and never break mid-word). A vendor word ("AWS",
    "Amazon") stays on the same line as the word after it."""
    words = label.split(" ")
    if len(label) <= MAX_LINE_CHARS or len(words) == 1:
        return label

    first_split = 2 if words[0] in VENDOR_WORDS else 1
    if first_split >= len(words):  # "Amazon CodeCatalyst": one long line beats a split vendor name
        return label

    split = min(
        range(first_split, len(words)),
        key=lambda i: max(len(" ".join(words[:i])), len(" ".join(words[i:]))),
    )
    return " ".join(words[:split]) + "\n" + " ".join(words[split:])
