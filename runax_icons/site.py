"""A static site of the packs for agents and people: the libraries, `index.json` and `llms.txt`.

Hosted anywhere (GitHub Pages, say), it lets an agent in any repository draw with the icons using
only what `llms.txt` explains: no tool to install, no repository to clone.
"""

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .icon import Icon
from .packs import Pack

TITLE = "runax Excalidraw icons"
SUMMARY = (
    "Icon libraries for Excalidraw architecture diagrams: AWS, Azure, Kubernetes, Cloudflare, "
    "networking, data, observability, AI, Supabase and technology logos. Each icon is an image "
    "with its name as a caption below, grouped."
)
USAGE = """## Using an icon in a diagram

Every `.excalidrawlib` here is JSON with `libraryItems` (each a `name` and its `elements`: an
`image` element and its caption, a `text` element, grouped) and a top-level `files` map holding
the images, keyed by each image element's `fileId`. Excalidraw's library panel ignores that
`files` map, so to draw, write the `.excalidraw` file itself:

1. Pick icons by name from [index.json]({index}), and download the libraries of their packs.
   Libraries can be megabytes (AWS, Azure): filter them with code (jq, Python) by item `name`
   rather than reading them whole. Labels are full product names
   ("Amazon Simple Storage Service", not "Amazon S3"): search case-insensitively for part of the
   name, and of several matches prefer the shortest label, the service itself.
2. Copy each item's `elements` into the drawing's `elements`, moving every element of the item by
   the same `x`/`y` offset to place it. Icons differ in size (AWS: 64px services, 48px
   resources, 32px groups; most others 64px), so line them up by their centers. If the same
   icon is used twice, give the copy new unique `id`s and a new `groupIds` value.
3. Copy `files[fileId]` of each image element into the drawing's `files`, under the same id.
4. Connect icons with `arrow` elements. To keep an arrow attached when icons move, set its
   `startBinding`/`endBinding` to `{"elementId": <image id>, "focus": 0, "gap": 8}` and add
   `{"id": <arrow id>, "type": "arrow"}` to that image's `boundElements`. To label an arrow, add a
   `text` element with `containerId` set to the arrow's id, and `{"id": <text id>, "type":
   "text"}` to the arrow's `boundElements`.

A drawing is `{"type": "excalidraw", "version": 2, "source": "https://excalidraw.com",
"elements": [...], "appState": {"viewBackgroundColor": "#ffffff"}, "files": {...}}`. It embeds its
images, so it opens anywhere.

`index.json` lists `packs`, each with `name`, `title`, `license` (its terms), `forbid`
(operations its terms rule out, with reasons), `library` and `scene` (URLs), `icons` (a count) and
`labels` (every icon's name, which is also its item's `name` in the library); a pack with a
native-shape library has its URL in `native`. A
`scene` is an `.excalidraw` drawing of every icon in the library, for people to copy from.

Libraries named `-native` draw their icons with Excalidraw shapes instead of images: their items
need no `files`, and they also work in Excalidraw's library panel.
"""
TERMS = """## Terms

The icons belong to their owners and keep their terms: AWS and Azure icons may be used in
architecture diagrams, training material and documentation, unmodified, with the service name
next to the icon; product logos are trademarks, used to refer to their products. Each pack's
terms are in `index.json` (`license`) and its README.
"""


@dataclass(frozen=True)
class Library:
    """One published library and what's in it."""

    path: str  # relative to the site root
    labels: list[str]

    def entry(self) -> dict[str, Any]:
        return {"library": self.path, "icons": len(self.labels), "labels": self.labels}


class SiteExporter:
    """Writes the site for built packs into `out` (replacing what was there)."""

    def __init__(self, packs: list[Pack], out: Path, base_url: str = ""):
        self.packs = packs
        self.out = out
        self.base_url = base_url.rstrip("/") + "/" if base_url else ""

    def export(self) -> int:
        """Write everything; return how many files were published."""
        shutil.rmtree(self.out, ignore_errors=True)
        self.out.mkdir(parents=True)

        index = [self._pack(pack) for pack in self.packs]
        (self.out / "index.json").write_text(
            json.dumps({"title": TITLE, "packs": index}, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        (self.out / "llms.txt").write_text(self._llms_txt(index), encoding="utf-8")
        return sum(1 for f in self.out.rglob("*") if f.is_file())

    def _pack(self, pack: Pack) -> dict[str, Any]:
        icons = pack.icons()
        entry: dict[str, Any] = {
            "name": pack.name,
            "title": pack.config.title,
            "license": pack.config.license.strip(),
            "forbid": {str(op): reason for op, reason in pack.config.forbid.forbidden.items()},
            **self._publish(pack, pack.library_path, pack.scene_path, icons).entry(),
            "scene": self._link(pack, pack.scene_path),
        }
        if pack.config.publish and pack.native_library_path.exists():
            entry["native"] = self._publish(pack, pack.native_library_path, None, []).path
        return entry

    def _publish(self, pack: Pack, library: Path, scene: Path | None, icons: list[Icon]) -> Library:
        if not library.exists():
            raise FileNotFoundError(f"{library} isn't built: run `runax-icons build {pack.name}`")
        for file in (library, scene):
            if file:
                target = self.out / pack.name / file.name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(file, target)
        return Library(self._link(pack, library), [pack.label(icon) for icon in icons])

    def _link(self, pack: Pack, file: Path) -> str:
        return f"{self.base_url}{pack.name}/{file.name}"

    def _llms_txt(self, index: list[dict[str, Any]]) -> str:
        lines = [f"# {TITLE}", "", f"> {SUMMARY}", "", USAGE.replace("{index}", f"{self.base_url}index.json"), TERMS, "## Packs", ""]
        for pack in index:
            line = f"- [{pack['title']}]({pack['library']}): {_icons(pack['icons'])}"
            if pack.get("native"):
                line += f"; native shapes: [{pack['native'].rsplit('/', 1)[-1]}]({pack['native']})"
            lines.append(line)
        lines += ["", "## Index", "", f"- [index.json]({self.base_url}index.json): every pack, library and icon name", ""]
        return "\n".join(lines)


def _icons(count: int) -> str:
    return f"{count} icon" if count == 1 else f"{count} icons"
