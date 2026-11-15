import re
from pathlib import Path

from ..icon import Icon
from .elements import ICON_SIZE, Element, ElementFactory
from .geometry import Box, Point
from .scene import Scene

PLACEMENT_GAP = 96  # space between an icon added without a position and the drawing's right edge
ARROW_GAP = 8  # space between an arrow's end and the icon it's bound to
ARROW_WIDTH = 2


class DiagramError(Exception):
    pass


class Diagram:
    """An .excalidraw file being edited: pack icons are added to it and connected by label.

    An icon in a diagram is an image grouped with one text element, the shape this package
    (and its libraries) create; its label is that text.
    """

    def __init__(self, path: Path, factory: ElementFactory):
        self.path = path
        self.factory = factory
        self.scene = Scene.load(path) if path.exists() else Scene()

    def save(self) -> None:
        self.scene.save(self.path)

    def add_icon(
        self, icon: Icon, label: str, at: Point | None = None, box: int = ICON_SIZE
    ) -> Point:
        """Add the icon and its label as one group, with its SVG embedded so the diagram
        renders without the library. Without a position it goes right of the drawing."""
        at = at or self._free_spot()
        self.scene.add_icon(self.factory, icon, label, at.x, at.y, box)
        return at

    def connect(
        self,
        source: str,
        target: str,
        label: str | None = None,
        dashed: bool = False,
        color: str = "#1e1e1e",
    ) -> None:
        """An arrow from one icon to another, found by label and bound to both images, so it
        follows them when they're moved in Excalidraw."""
        start, end = self.find_icon(source), self.find_icon(target)
        if start["id"] == end["id"]:
            raise DiagramError(f"can't connect {source!r} to itself")

        # Aim from group center to group center, clipped to each icon's box (image and caption).
        start_box, end_box = self._group_box(start), self._group_box(end)
        start_point = start_box.edge_toward(end_box.center, ARROW_GAP)
        end_point = end_box.edge_toward(start_box.center, ARROW_GAP)

        arrow = self.factory.arrow(
            start_point,
            end_point,
            start["id"],
            end["id"],
            ARROW_GAP,
            stroke_color=color,
            stroke_width=ARROW_WIDTH,
            stroke_style="dashed" if dashed else "solid",
        )
        for image in (start, end):
            image["boundElements"] = (image.get("boundElements") or []) + [
                {"id": arrow.id, "type": "arrow"}
            ]

        elements: list[Element] = [arrow]
        if label:
            middle = Point((start_point.x + end_point.x) / 2, (start_point.y + end_point.y) / 2)
            text = self.factory.text(label, middle.x, middle.y, container_id=arrow.id)
            text.y -= text.height / 2
            arrow.bound_elements = [{"id": text.id, "type": "text"}]
            elements.append(text)

        self.scene.add(elements)

    def icons(self) -> dict[str, list[dict]]:
        """Normalized label -> image elements of the icons with that label."""
        by_group: dict[str, list[dict]] = {}
        for element in self.scene.visible:
            for group in element.get("groupIds", []):
                by_group.setdefault(group, []).append(element)

        icons: dict[str, list[dict]] = {}
        for members in by_group.values():
            images = [e for e in members if e["type"] == "image"]
            texts = [e for e in members if e["type"] == "text"]
            if len(images) == 1 and len(texts) == 1:
                icons.setdefault(_normalize(texts[0]["originalText"]), []).append(images[0])

        return icons

    def find_icon(self, label: str) -> dict:
        icons = self.icons()
        matches = icons.get(_normalize(label), [])
        if not matches:
            known = ", ".join(sorted(icons)) or "none"
            raise DiagramError(f"no icon labeled {label!r} in {self.path.name} (icons: {known})")
        if len(matches) > 1:
            raise DiagramError(
                f"{len(matches)} icons are labeled {label!r} in {self.path.name}; rename one"
            )

        return matches[0]

    def _group_box(self, image: dict) -> Box:
        group = image["groupIds"][0]
        return Box.around([e for e in self.scene.visible if group in e.get("groupIds", [])])

    def _free_spot(self) -> Point:
        if not self.scene.visible:
            return Point(0, 0)

        box = Box.around(self.scene.visible)
        return Point(round(box.right + PLACEMENT_GAP), round(box.top))


def _normalize(text: str) -> str:
    """Labels compare case-insensitively and ignore wrapping (captions wrap long names)."""
    return re.sub(r"\s+", " ", text).strip().lower()
