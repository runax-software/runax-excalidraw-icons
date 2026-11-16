import copy
import re
from pathlib import Path

from ..icon import Icon
from .elements import ICON_SIZE, Element, ElementFactory, wrap_label
from .geometry import Box, Point
from .library_file import LibraryItem
from .scene import Scene

PLACEMENT_GAP = 96  # space between an icon added without a position and the drawing's right edge
ARROW_GAP = 8  # space between an arrow's end and the icon it's bound to
ARROW_WIDTH = 2
# Element types Excalidraw can bind an arrow to (lines and freedraw it can't).
BINDABLE = {"rectangle", "ellipse", "diamond", "image", "text", "frame", "embeddable", "iframe"}


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

    def add_library_item(self, item: LibraryItem, at: Point | None = None, label: str | None = None) -> Point:
        """Add a library item: its elements with fresh ids (so the same item can be added twice),
        moved so its top-left is `at` (default: right of the drawing), and its image files.
        `label` replaces the caption of an item that has exactly one text element."""
        at = at or self._free_spot()
        box = Box.around(item.elements)
        ids: dict[str, str] = {}
        groups: dict[str, str] = {}

        def new_id(old: str, table: dict[str, str]) -> str:
            return table.setdefault(old, self.factory.new_id())

        elements = []
        for original in item.elements:
            e = copy.deepcopy(original)
            e["id"] = new_id(e["id"], ids)
            e["x"] += at.x - box.left
            e["y"] += at.y - box.top
            e["groupIds"] = [new_id(g, groups) for g in e.get("groupIds", [])]
            e["frameId"] = None
            e["updated"] = self.factory.now
            e["seed"], e["versionNonce"] = self.factory.seed(), self.factory.seed()
            elements.append(e)

        # References between the item's elements follow the new ids; outside ones are dropped.
        for e in elements:
            if e.get("containerId"):
                e["containerId"] = ids.get(e["containerId"])
            if e.get("boundElements"):
                e["boundElements"] = [{**b, "id": ids[b["id"]]} for b in e["boundElements"] if b["id"] in ids] or None
            for key in ("startBinding", "endBinding"):
                if e.get(key):
                    target = ids.get(e[key].get("elementId", ""))
                    e[key] = {**e[key], "elementId": target} if target else None

        texts = [e for e in elements if e["type"] == "text"]
        if label and len(texts) == 1:
            caption = texts[0]
            center = caption["x"] + caption["width"] / 2
            sized = self.factory.text(wrap_label(label), center, caption["y"])  # wrapped and measured like ours
            caption.update(text=sized.text, originalText=sized.text, x=sized.x, width=sized.width, height=sized.height)

        self.scene.elements += elements
        self.scene.files.update(item.files)
        return at

    def connect(
        self,
        source: str,
        target: str,
        label: str | None = None,
        dashed: bool = False,
        color: str = "#1e1e1e",
    ) -> None:
        """An arrow from one icon to another, found by label. It's bound to each icon's image or
        main shape, so it follows them when they're moved in Excalidraw; icons drawn with lines
        (which Excalidraw can't bind to) get an unbound arrow."""
        start, end = self.find_icon(source), self.find_icon(target)
        if start["id"] == end["id"]:
            raise DiagramError(f"can't connect {source!r} to itself")

        # Aim from group center to group center, clipped to each icon's box (image and caption).
        start_box, end_box = self._group_box(start), self._group_box(end)
        start_point = start_box.edge_toward(end_box.center, ARROW_GAP)
        end_point = end_box.edge_toward(start_box.center, ARROW_GAP)

        bindable = [e for e in (start, end) if e["type"] in BINDABLE]
        arrow = self.factory.arrow(
            start_point,
            end_point,
            start["id"] if start in bindable else None,
            end["id"] if end in bindable else None,
            ARROW_GAP,
            stroke_color=color,
            stroke_width=ARROW_WIDTH,
            stroke_style="dashed" if dashed else "solid",
        )
        for image in bindable:
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
        """Normalized label -> the main element of each icon with that label.

        An icon is a group with exactly one text element, its caption: an image with its label,
        or any library item drawn with shapes. Its main element, what arrows attach to, is its
        image, else its largest bindable shape, else its largest shape."""
        by_group: dict[str, list[dict]] = {}
        for element in self.scene.visible:
            if element.get("groupIds"):
                by_group.setdefault(element["groupIds"][-1], []).append(element)  # outermost group

        icons: dict[str, list[dict]] = {}
        for members in by_group.values():
            texts = [e for e in members if e["type"] == "text"]
            shapes = [e for e in members if e["type"] != "text"]
            if len(texts) != 1 or not shapes:
                continue
            images = [e for e in shapes if e["type"] == "image"]
            bindable = [e for e in shapes if e["type"] in BINDABLE]
            main = images[0] if len(images) == 1 else max(bindable or shapes, key=lambda e: e["width"] * e["height"])
            icons.setdefault(_normalize(texts[0].get("originalText", texts[0].get("text", ""))), []).append(main)

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
        group = image["groupIds"][-1]
        return Box.around([e for e in self.scene.visible if group in e.get("groupIds", [])])

    def _free_spot(self) -> Point:
        if not self.scene.visible:
            return Point(0, 0)

        box = Box.around(self.scene.visible)
        return Point(round(box.right + PLACEMENT_GAP), round(box.top))


def _normalize(text: str) -> str:
    """Labels compare case-insensitively and ignore wrapping (captions wrap long names)."""
    return re.sub(r"\s+", " ", text).strip().lower()
