import json
from pathlib import Path
from typing import Any

from ..icon import Icon
from .elements import ICON_SIZE, Element, ElementFactory

SOURCE = "https://excalidraw.com"


class Scene:
    """An .excalidraw document: its elements and the files (images) they reference.

    Elements are kept as Excalidraw's own JSON objects, so a scene loaded from a file keeps
    every element it had, including kinds this package never creates.
    """

    def __init__(self, elements: list[dict] | None = None, files: dict[str, dict] | None = None):
        self.elements = elements if elements is not None else []
        self.files = files if files is not None else {}

    @classmethod
    def load(cls, path: Path) -> "Scene":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(data.get("elements", []), data.get("files", {}))

    def save(self, path: Path, indent: int | None = 2) -> None:
        path.write_text(json.dumps(self.to_dict(), indent=indent), encoding="utf-8")

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "excalidraw",
            "version": 2,
            "source": SOURCE,
            "elements": self.elements,
            "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None},
            "files": self.files,
        }

    @property
    def visible(self) -> list[dict]:
        return [e for e in self.elements if not e.get("isDeleted")]

    def add(self, elements: list[Element]) -> None:
        self.elements += [e.to_dict() for e in elements]

    def add_icon(
        self, factory: ElementFactory, icon: Icon, label: str, x: float, y: float, box: int = ICON_SIZE
    ) -> None:
        """The icon with its label, and its SVG embedded so the scene renders on its own."""
        self.add(factory.icon(icon, label, x, y, box))
        self.files[icon.file_id] = factory.file(icon)


class Library:
    """An .excalidrawlib: one item per icon.

    excalidraw.com's library format has no place for binary files: items reference their SVG
    by `fileId`, and the SVG data is also written to a top-level `files` map, but excalidraw.com
    ignores that map on import. The pack's scene embeds the same files under the same
    (deterministic) fileIds, so library items render once the scene's images are loaded.
    """

    def __init__(self, factory: ElementFactory):
        self.factory = factory
        self.items: list[dict] = []
        self.files: dict[str, dict] = {}

    def add_icon(self, icon: Icon, label: str, box: int = ICON_SIZE) -> None:
        self.items.append(
            {
                "id": self.factory.new_id(),
                "status": "unpublished",
                "elements": [e.to_dict() for e in self.factory.icon(icon, label, box=box)],
                "created": self.factory.now,
                "name": label,
            }
        )
        self.files[icon.file_id] = self.factory.file(icon)

    def save(self, path: Path) -> None:
        data = {
            "type": "excalidrawlib",
            "version": 2,
            "source": SOURCE,
            "libraryItems": self.items,
            "files": self.files,  # ignored by excalidraw.com; see the class docstring
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
