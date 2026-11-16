from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

from ..excalidraw.elements import ICON_SIZE
from ..icon import Icon
from ..sources import FolderSource
from .config import PackConfig, SourceEntry
from .imports import ImportTarget
from .restrictions import Restrictions

OUTPUT_PREFIX = "runax-"  # published file names: runax-<pack>.excalidrawlib


@dataclass
class Pack:
    """A folder with a pack.yml: its config, its icons in src/, and where its outputs go."""

    dir: Path
    config: PackConfig

    @classmethod
    def load(cls, dir: Path) -> "Pack":
        return cls(dir, PackConfig.load(dir / "pack.yml"))

    @property
    def name(self) -> str:
        return self.dir.name

    @property
    def src_dir(self) -> Path:
        return self.dir / "src"

    @property
    def library_path(self) -> Path:
        return self.dir / f"{OUTPUT_PREFIX}{self.name}.excalidrawlib"

    @property
    def native_library_path(self) -> Path:
        """The library of native shapes, built unless the pack forbids `native`."""
        return self.dir / f"{OUTPUT_PREFIX}{self.name}-native.excalidrawlib"

    @property
    def scene_path(self) -> Path:
        return self.dir / f"{OUTPUT_PREFIX}{self.name}.excalidraw"

    @property
    def readme_path(self) -> Path:
        return self.dir / "README.md"

    @property
    def changelog_path(self) -> Path:
        return self.dir / "CHANGELOG.md"

    def icons(self) -> list[Icon]:
        """Every icon in src/, sorted by label."""
        if not self.src_dir.exists():
            return []
        return sorted(FolderSource(self.src_dir), key=lambda icon: self.label(icon).lower())

    def label(self, icon: Icon) -> str:
        return icon.label(self.config.labels)

    def box(self, icon: Icon) -> int:
        """The square an icon is drawn in: its designed size for `native_size` packs (some
        vendors, AWS among them, ask for icons at their predefined size), else ICON_SIZE."""
        if not self.config.native_size:
            return ICON_SIZE
        return icon.size or ICON_SIZE

    @cached_property
    def import_targets(self) -> list[ImportTarget]:
        return [target for entry in self.config.imports for target in entry.targets()]

    def restrictions(self, icon: Icon) -> Restrictions:
        """What the icon may not be put through: the pack's `forbid:` and its entry's."""
        entry = self.source_of(icon)
        return self.config.forbid | (entry.forbid if entry else Restrictions())

    def source_of(self, icon: Icon) -> ImportTarget | SourceEntry | None:
        """The import or `sources` entry an icon came from. Imports come first; among
        `sources` entries the first whose glob matches wins."""
        path = icon.path.as_posix()
        return next((t for t in self.import_targets if t.covers(path)), None) or next(
            (s for s in self.config.sources if s.covers(path)), None
        )
