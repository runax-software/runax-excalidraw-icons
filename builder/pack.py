import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .exporter import ExcalidrawExporter
from .readme import ReadmeRenderer
from .source import IconSource


@dataclass
class Pack:
    """A folder with a pack.yml: its config, downloads, stored icons and generated files."""

    name: str
    dir: Path
    title: str
    source: str  # markdown, shown in the README
    download: str  # glob in downloads/; the newest match wins
    labels: dict = field(default_factory=dict)  # lowercased file name -> label
    samples: list = field(default_factory=list)  # labels previewed in the README

    @classmethod
    def load(cls, pack_yml):
        config = yaml.safe_load(pack_yml.read_text(encoding="utf-8"))
        return cls(name=pack_yml.parent.name, dir=pack_yml.parent, **config)

    @classmethod
    def discover(cls, root):
        return [cls.load(path) for path in sorted(root.glob("*/pack.yml"))]

    @property
    def icons_dir(self):
        return self.dir / "icons"

    @property
    def downloads_dir(self):
        return self.dir / "downloads"

    @property
    def library_path(self):
        return self.dir / f"{self.name}.excalidrawlib"

    @property
    def scene_path(self):
        return self.dir / f"{self.name}.excalidraw"

    @property
    def readme_path(self):
        return self.dir / "README.md"

    def resolve_source(self):
        """Newest matching download, otherwise the stored icons; None if neither exists."""
        downloads = sorted(
            self.downloads_dir.glob(self.download), key=lambda p: p.stat().st_mtime
        )
        path = downloads[-1] if downloads else self.icons_dir

        return IconSource.open(path) if path.exists() else None

    def select_icons(self, source):
        """Best variant of each icon, minus white-only ones, sorted by label."""
        best = {}
        for icon in source:
            if icon.is_white_only:
                continue

            if icon.key not in best or icon.rank > best[icon.key].rank:
                best[icon.key] = icon

        return sorted(best.values(), key=lambda icon: icon.label(self.labels).lower())

    def store_icons(self, icons):
        shutil.rmtree(self.icons_dir, ignore_errors=True)

        for icon in icons:
            target = self.icons_dir / icon.path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(icon.svg)

    def build(self, now):
        source = self.resolve_source()
        if source is None:
            print(f"[{self.name}] skipped: no downloads/{self.download} and no icons/")
            return

        icons = self.select_icons(source)
        if source.path != self.icons_dir:
            self.store_icons(icons)

        items = [(icon, icon.label(self.labels)) for icon in icons]
        exporter = ExcalidrawExporter(now)

        self.library_path.write_text(
            json.dumps(exporter.library(items), indent=2), encoding="utf-8"
        )
        self.scene_path.write_text(json.dumps(exporter.scene(items)), encoding="utf-8")
        self.readme_path.write_text(
            ReadmeRenderer().render(self, icons), encoding="utf-8"
        )

        root = self.dir.parent
        print(
            f"[{self.name}] packaged {len(icons)} icons from {source.path.relative_to(root)} -> {self.library_path.relative_to(root)}"
        )
