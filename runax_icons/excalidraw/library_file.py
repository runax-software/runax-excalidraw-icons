"""Reading .excalidrawlib files, so their items can be searched and placed into diagrams.

Any library works: ours (image items, whose SVGs are in the file's `files` map), native-shape
libraries, or one downloaded from anywhere. Excalidraw itself ignores a library's `files` when
importing it; reading them here is what lets image items be used outside its library panel.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class LibraryItem:
    """One item: its name, its elements, and the image files those elements use."""

    name: str
    elements: list[dict[str, Any]]
    files: dict[str, dict[str, Any]] = field(default_factory=dict)
    library: Path | None = None


class LibraryFile:
    """An .excalidrawlib's items."""

    def __init__(self, path: Path):
        self.path = path
        data = json.loads(path.read_text(encoding="utf-8"))
        # v2 libraries have `libraryItems`; v1 ones a list of element lists under `library`.
        raw = data.get("libraryItems") or [{"elements": elements} for elements in data.get("library", [])]
        shared_files: dict[str, dict[str, Any]] = data.get("files") or {}
        self.items = [self._item(entry, shared_files) for entry in raw]

    def _item(self, entry: dict[str, Any], shared_files: dict[str, dict[str, Any]]) -> LibraryItem:
        elements = [e for e in entry.get("elements", []) if not e.get("isDeleted")]
        own_files = entry.get("files") or {}
        files = {
            file_id: own_files.get(file_id) or shared_files[file_id]
            for e in elements
            if (file_id := e.get("fileId")) and (file_id in own_files or file_id in shared_files)
        }
        return LibraryItem(entry.get("name") or "", elements, files, self.path)
