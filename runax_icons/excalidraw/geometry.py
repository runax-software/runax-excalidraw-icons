import math
from dataclasses import dataclass
from typing import NamedTuple


class Point(NamedTuple):
    x: float
    y: float


@dataclass(frozen=True)
class Box:
    left: float
    top: float
    right: float
    bottom: float

    @classmethod
    def around(cls, elements: list[dict]) -> "Box":
        """The bounds of Excalidraw elements (their x, y, width and height)."""
        return cls(
            min(e["x"] for e in elements),
            min(e["y"] for e in elements),
            max(e["x"] + e["width"] for e in elements),
            max(e["y"] + e["height"] for e in elements),
        )

    @property
    def center(self) -> Point:
        return Point((self.left + self.right) / 2, (self.top + self.bottom) / 2)

    def edge_toward(self, target: Point, gap: float = 0) -> Point:
        """Where the line from this box's center to `target` leaves the box, plus `gap`."""
        center = self.center
        dx, dy = target.x - center.x, target.y - center.y
        length = math.hypot(dx, dy) or 1
        half_w, half_h = (self.right - self.left) / 2, (self.bottom - self.top) / 2

        scale = min(
            half_w / abs(dx) if dx else math.inf,
            half_h / abs(dy) if dy else math.inf,
        )
        return Point(
            center.x + dx * scale + dx / length * gap,
            center.y + dy * scale + dy / length * gap,
        )
