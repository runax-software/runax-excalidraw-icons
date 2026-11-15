import json
import shutil
import tarfile
import tempfile
import zipfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from fnmatch import fnmatch
from pathlib import Path

import yaml

from . import transform
from .exporter import ExcalidrawExporter
from .fetch import fetch
from .readme import ReadmeRenderer
from .source import FolderSource, IconSource

DOWNLOAD_WORKERS = 8
OUTPUT_PREFIX = "runax-"  # published file names: runax-<pack>.excalidrawlib


@dataclass
class Pack:
    """A folder with a pack.yml: its config, source SVGs and generated files."""

    name: str
    dir: Path
    title: str
    source: str  # markdown, shown in the README
    imports: list = field(default_factory=list)  # `import:`; see import_icons
    downloaded: str = ""  # when the imports were last fetched, shown in the README
    sources: list = field(default_factory=list)  # hand-made files: {files, url, note}
    labels: dict = field(default_factory=dict)  # lowercased file name -> label
    samples: list = field(default_factory=list)  # labels previewed in the README

    @classmethod
    def load(cls, pack_yml):
        config = yaml.safe_load(pack_yml.read_text(encoding="utf-8"))
        if "downloaded" in config:
            config["downloaded"] = str(config["downloaded"])  # YAML reads dates as date
        if "import" in config:
            config["imports"] = config.pop("import")  # `import` is a Python keyword

        return cls(name=pack_yml.parent.name, dir=pack_yml.parent, **config)

    @classmethod
    def discover(cls, root):
        return [cls.load(path) for path in sorted(root.glob("*/pack.yml"))]

    @property
    def src_dir(self):
        return self.dir / "src"

    @property
    def library_path(self):
        return self.dir / f"{OUTPUT_PREFIX}{self.name}.excalidrawlib"

    @property
    def scene_path(self):
        return self.dir / f"{OUTPUT_PREFIX}{self.name}.excalidraw"

    @property
    def readme_path(self):
        return self.dir / "README.md"

    @staticmethod
    def is_archive_import(entry):
        """Archive imports fill a folder (`into` is a folder or all of src/); file imports
        write one file (`into` is an .svg path)."""
        return not entry.get("into", "").endswith(".svg")

    def expanded_imports(self):
        """`import:` entries with every `names:` template expanded to one entry per name.

        `names` is a list, or a map of name -> src; `{name}` and `{src}` in `url` and `into`
        are replaced (for a list, both are the name)."""
        for entry in self.imports:
            names = entry.get("names")
            if names is None:
                yield entry
                continue

            pairs = names.items() if isinstance(names, dict) else ((n, n) for n in names)
            for name, src in pairs:
                yield {
                    **entry,
                    "url": entry["url"].format(name=name, src=src),
                    "into": entry["into"].format(name=name, src=src),
                }

    def select_icons(self, source):
        """Best variant of each icon, minus white-only ones."""
        best = {}
        for icon in source:
            if icon.is_white_only:
                continue

            if icon.key not in best or icon.rank > best[icon.key].rank:
                best[icon.key] = icon

        return list(best.values())

    def import_icons(self):
        """Download every `import:` url (into a temporary folder) and write the results to src/.

        An archive (zip or tar) replaces the folder src/<into> with the best variant of each
        icon under its optional `path`. A single SVG or PNG is written to src/<into> after the
        entry's edits (see transform.apply)."""
        entries = list(self.expanded_imports())
        if not entries:
            return

        with tempfile.TemporaryDirectory() as tmp:
            urls = list(dict.fromkeys(entry["url"] for entry in entries))
            with ThreadPoolExecutor(DOWNLOAD_WORKERS) as pool:
                files = dict(zip(urls, pool.map(lambda url: fetch(url, Path(tmp)), urls)))

            for entry in entries:
                if self.is_archive_import(entry):
                    self._import_archive(entry, files[entry["url"]])
                else:
                    target = self.src_dir / entry["into"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(transform.apply(files[entry["url"]].read_bytes(), entry))

        files_imported = sum(not self.is_archive_import(e) for e in entries)
        if files_imported:
            print(f"[{self.name}] imported {files_imported} files")

    def _import_archive(self, entry, archive):
        if not (zipfile.is_zipfile(archive) or tarfile.is_tarfile(archive)):
            raise ValueError(f"[{self.name}] {entry['url']} is not a zip or tar archive")

        icons = self.select_icons(IconSource.open(archive, entry.get("path")))
        if not icons:
            raise ValueError(f"[{self.name}] no icons in {entry['url']} under {entry.get('path')!r}")

        target = self.src_dir / entry.get("into", "")
        shutil.rmtree(target, ignore_errors=True)
        for icon in icons:
            path = target / icon.path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(icon.svg)

        print(f"[{self.name}] imported {len(icons)} icons -> {target.relative_to(self.dir.parent)}")

    def source_of(self, icon):
        """The import or `sources` entry an icon came from, or None. Imports come first; a
        `sources` entry matches by its `files` glob, the first match wins."""
        path = icon.path.as_posix()
        for entry in self.expanded_imports():
            into = entry.get("into", "")
            if self.is_archive_import(entry):
                if not into or path.startswith(into.rstrip("/") + "/"):
                    return entry
            elif path == into:
                return entry

        return next((s for s in self.sources if fnmatch(path, s["files"])), None)

    def check_sources(self, icons):
        """Warn about icons nothing covers, `sources` entries that match no icon, and
        imported files missing from src/."""
        unsourced = [icon.path.as_posix() for icon in icons if not self.source_of(icon)]
        if unsourced:
            print(f"[{self.name}] icons without a source: {', '.join(unsourced)}")

        used = {id(self.source_of(icon)) for icon in icons}
        unused = [s["files"] for s in self.sources if id(s) not in used]
        if unused:
            print(f"[{self.name}] sources matching no icon: {', '.join(unused)}")

        missing = [
            e["into"]
            for e in self.expanded_imports()
            if not self.is_archive_import(e) and not (self.src_dir / e["into"]).exists()
        ]
        if missing:
            print(f"[{self.name}] not in src/, run with --import: {', '.join(missing)}")

    def source_rows(self):
        """(files, url, notes) for the README: each `import:` entry, then each `sources` entry."""
        for entry in self.imports:
            notes = [entry.get("note", ""), transform.describe(entry)]
            if self.is_archive_import(entry):
                into = entry.get("into", "")
                files = f"{into}/**" if into else "**"
                notes.append("largest size of each icon, white-only ones skipped")
                if entry.get("path"):
                    notes.append(f"from `{entry['path']}` in the archive")
            else:
                files = entry["into"].format(name="*", src="*")
                if "names" in entry:
                    notes.append(f"{len(entry['names'])} files")

            yield files, entry["url"], "; ".join(n for n in notes if n)

        for s in self.sources:
            yield s["files"], s.get("url", ""), s.get("note", "")

    def build(self, now):
        if not self.src_dir.exists():
            print(f"[{self.name}] skipped: no src/")
            return

        icons = sorted(
            FolderSource(self.src_dir), key=lambda icon: icon.label(self.labels).lower()
        )
        self.check_sources(icons)

        items = [(icon, icon.label(self.labels)) for icon in icons]
        exporter = ExcalidrawExporter(now)

        self.library_path.write_text(
            json.dumps(exporter.library(items), indent=2), encoding="utf-8"
        )
        self.scene_path.write_text(json.dumps(exporter.scene(items)), encoding="utf-8")
        self.readme_path.write_text(
            ReadmeRenderer().render(self, icons), encoding="utf-8"
        )

        print(
            f"[{self.name}] packaged {len(icons)} icons -> {self.library_path.relative_to(self.dir.parent)}"
        )
