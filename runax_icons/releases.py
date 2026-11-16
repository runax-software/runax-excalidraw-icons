"""Packs released as GitHub Releases, for agents in other repositories.

Each pack is released on its own, tagged `<pack>/vX.Y.Z`, with its libraries, its scene and a
`runax-<pack>.json` entry describing them. The `index` release merges the latest entry of every
pack into `index.json` and an `llms.txt` that explains to an agent how to download and use them
with `gh`: no clone, no tooling, nothing published on libraries.excalidraw.com.
"""

import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .packs import Pack

INDEX_TAG = "index"
ENTRY_SUFFIX = ".json"
TAG = re.compile(r"^(?P<pack>[a-z0-9-]+)/v(?P<version>\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?)$")
SECTION = re.compile(r"^## \[(?P<version>[^\]]+)\].*$", re.MULTILINE)

TITLE = "runax Excalidraw icons"
SUMMARY = (
    "Icon libraries for Excalidraw architecture diagrams: AWS, Azure, Kubernetes, Cloudflare, "
    "networking, data, observability, AI, Supabase and technology logos. Each icon is an image "
    "with its name as a caption below, grouped."
)
USAGE = """## Downloading

Everything is a GitHub Release asset of `{repo}`, downloaded with the GitHub CLI (`gh`, logged
in with access to the repository):

```sh
gh release download {index_tag} -R {repo} -p index.json -O -       # this index, as JSON
gh release download aws/v1.0.0 -R {repo} -p runax-aws.excalidrawlib -D /tmp/icons
```

Each pack is released on its own: its `release` is the tag to download from, and `library`,
`scene` and `native` are file names in that release.

## Using an icon in a diagram

Every `.excalidrawlib` is JSON with `libraryItems` (each a `name` and its `elements`: an `image`
element and its caption, a `text` element, grouped) and a top-level `files` map holding the
images, keyed by each image element's `fileId`. Excalidraw's library panel ignores that `files`
map, so to draw, write the `.excalidraw` file itself:

1. Pick icons by name from `index.json`, and download the libraries of their packs. Libraries
   can be megabytes (AWS, Azure): filter them with code (jq, Python) by item `name` rather than
   reading them whole. Labels are full product names ("Amazon Simple Storage Service", not
   "Amazon S3"): search case-insensitively for part of the name, and of several matches prefer
   the shortest label, the service itself.
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

`index.json` lists `packs`, each with `name`, `title`, `release`, `version`, `license` (its
terms), `forbid` (operations its terms rule out, with reasons), `library` and `scene` (file
names), `icons` (a count) and `labels` (every icon's name, which is also its item's `name` in the
library) and `native`, the file name of its native-shape library. A `scene` is an
`.excalidraw` drawing of every icon in the library, for people to copy from.

Libraries named `-native` draw their icons with Excalidraw shapes instead of images: their items
need no `files`, and they also work in Excalidraw's library panel.
"""
TERMS = """## Terms

The icons belong to their owners and keep their terms: AWS and Azure icons may be used in
architecture diagrams, training material and documentation, unmodified, with the service name
next to the icon; product logos are trademarks, used to refer to their products. Each pack's
terms are in `index.json` (`license`) and its README.
"""


class ReleaseError(Exception):
    """A tag that doesn't name a pack and version, or a version its changelog doesn't have."""


@dataclass(frozen=True)
class Tag:
    pack: str
    version: str

    @classmethod
    def parse(cls, tag: str) -> "Tag":
        match = TAG.match(tag)
        if not match:
            raise ReleaseError(f"{tag!r} isn't a pack release tag like aws/v1.0.0")
        return cls(match["pack"], match["version"])

    def __str__(self) -> str:
        return f"{self.pack}/v{self.version}"


class Changelog:
    """A Keep a Changelog file: the notes of one released version."""

    def __init__(self, path: Path):
        self.path = path
        self.text = path.read_text(encoding="utf-8") if path.exists() else ""

    def notes(self, version: str) -> str:
        sections = list(SECTION.finditer(self.text))
        for i, section in enumerate(sections):
            if section["version"] == version:
                end = sections[i + 1].start() if i + 1 < len(sections) else len(self.text)
                return self.text[section.end():end].strip() + "\n"
        raise ReleaseError(f"{self.path} has no `## [{version}]` section: add the release notes first")


class PackRelease:
    """One built pack's release assets: its libraries, its scene and its index entry."""

    def __init__(self, pack: Pack, tag: Tag):
        if tag.pack != pack.name:
            raise ReleaseError(f"tag {tag} is for pack {tag.pack!r}, not {pack.name!r}")
        self.pack = pack
        self.tag = tag

    def notes(self) -> str:
        return Changelog(self.pack.changelog_path).notes(self.tag.version)

    def write(self, out: Path) -> list[Path]:
        """Copy the assets into `out`; return them, the entry last."""
        out.mkdir(parents=True, exist_ok=True)
        files = [self.pack.library_path, self.pack.scene_path]
        if self.pack.native_library_path.exists():
            files.append(self.pack.native_library_path)

        assets = []
        for file in files:
            if not file.exists():
                raise ReleaseError(f"{file} isn't built: run `runax-icons build {self.pack.name}`")
            assets.append(Path(shutil.copyfile(file, out / file.name)))

        entry = out / f"{self.pack.library_path.stem}{ENTRY_SUFFIX}"
        entry.write_text(json.dumps(self.entry(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return [*assets, entry]

    def entry(self) -> dict[str, Any]:
        pack = self.pack
        labels = [pack.label(icon) for icon in pack.icons()]
        entry: dict[str, Any] = {
            "name": pack.name,
            "title": pack.config.title,
            "release": str(self.tag),
            "version": self.tag.version,
            "license": pack.config.license.strip(),
            "forbid": {str(op): reason for op, reason in pack.config.forbid.forbidden.items()},
            "library": pack.library_path.name,
            "scene": pack.scene_path.name,
            "icons": len(labels),
            "labels": labels,
        }
        if pack.native_library_path.exists():
            entry["native"] = pack.native_library_path.name
        return entry


class ReleaseIndex:
    """`index.json` and `llms.txt` from the entries of each pack's latest release."""

    def __init__(self, entries: list[dict[str, Any]], repo: str):
        self.entries = sorted(entries, key=lambda entry: entry["name"])
        self.repo = repo

    @classmethod
    def load(cls, folder: Path, repo: str) -> "ReleaseIndex":
        """Read every `runax-<pack>.json` entry in `folder`."""
        files = sorted(folder.glob(f"*{ENTRY_SUFFIX}"))
        entries = [json.loads(f.read_text(encoding="utf-8")) for f in files if f.name != "index.json"]
        return cls(entries, repo)

    def write(self, out: Path) -> list[Path]:
        out.mkdir(parents=True, exist_ok=True)
        index, llms = out / "index.json", out / "llms.txt"
        index.write_text(
            json.dumps({"title": TITLE, "repository": self.repo, "packs": self.entries}, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        llms.write_text(self.llms_txt(), encoding="utf-8")
        return [index, llms]

    def llms_txt(self) -> str:
        usage = USAGE.replace("{repo}", self.repo).replace("{index_tag}", INDEX_TAG)
        lines = [f"# {TITLE}", "", f"> {SUMMARY}", "", usage, TERMS, "## Packs", ""]
        for entry in self.entries:
            files = f"`{entry['library']}`"
            if entry.get("native"):
                files += f", native shapes `{entry['native']}`"
            lines.append(f"- {entry['title']} (`{entry['name']}`), release `{entry['release']}`: {files}, {_icons(entry['icons'])}")
        lines.append("")
        return "\n".join(lines)


def _icons(count: int) -> str:
    return f"{count} icon" if count == 1 else f"{count} icons"
