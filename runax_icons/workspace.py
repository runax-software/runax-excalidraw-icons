from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar
from pathlib import Path

from .excalidraw.library_file import LibraryFile, LibraryItem
from .icon import Icon
from .packs import Pack


class WorkspaceError(Exception):
    pass


class Workspace:
    """A folder of packs (every subfolder with a pack.yml)."""

    def __init__(self, root: Path):
        self.root = root

    def packs(self, names: list[str] | None = None) -> list[Pack]:
        """The packs named (all by default); unknown names are an error."""
        packs = [Pack.load(path.parent) for path in sorted(self.root.glob("*/pack.yml"))]
        if not packs:
            raise WorkspaceError(f"no packs (folders with a pack.yml) in {self.root}")

        unknown = set(names or []) - {pack.name for pack in packs}
        if unknown:
            raise WorkspaceError(f"unknown packs: {', '.join(sorted(unknown))}")

        return [pack for pack in packs if not names or pack.name in names]

    def catalog(self, pack: str | None = None) -> "IconCatalog":
        return IconCatalog(self.packs([pack] if pack else None))


class Match(ABC):
    """Something a catalog can find: a pack icon or a library item."""

    label: str

    @property
    @abstractmethod
    def source(self) -> str:
        """Where it comes from: a pack or a library file name."""

    @property
    @abstractmethod
    def search_name(self) -> str:
        """Also searched, besides the label (a file name)."""


@dataclass(frozen=True)
class IconMatch(Match):
    pack: Pack
    label: str
    icon: Icon

    @property
    def source(self) -> str:
        return self.pack.name

    @property
    def search_name(self) -> str:
        return self.icon.path.stem


@dataclass(frozen=True)
class LibraryMatch(Match):
    item: LibraryItem

    @property
    def label(self) -> str:  # type: ignore[override]
        return self.item.name

    @property
    def source(self) -> str:
        return self.item.library.name if self.item.library else "library"

    @property
    def search_name(self) -> str:
        return self.item.name


class IconNotFound(WorkspaceError):
    pass


class AmbiguousIcon(WorkspaceError):
    def __init__(self, text: str, candidates: list[Match]):
        super().__init__(f"{text!r} matches {len(candidates)} icons; use the full label")
        self.candidates = candidates


M = TypeVar("M", bound="Match")


class Catalog(Generic[M]):
    """Things found by label or file name: icons across packs, or items across libraries."""

    def __init__(self, matches: list[M]):
        self.matches = matches

    def search(self, text: str = "") -> list[M]:
        """Matches whose label or file name contains `text` (case-insensitive)."""
        needle = text.lower()
        return [m for m in self.matches if needle in m.label.lower() or needle in m.search_name.lower()]

    def resolve(self, text: str) -> M:
        """The one match `text` names: an exact label (case-insensitive), else a unique
        partial match."""
        found = self.search(text)
        candidates = [m for m in found if m.label.lower() == text.lower()] or found

        if not candidates:
            raise IconNotFound(f"no icon matches {text!r}; try `runax-icons search`")
        if len(candidates) > 1:
            raise AmbiguousIcon(text, list(candidates))
        return candidates[0]


class IconCatalog(Catalog[IconMatch]):
    """Every icon across some packs."""

    def __init__(self, packs: list[Pack]):
        super().__init__([IconMatch(pack, pack.label(icon), icon) for pack in packs for icon in pack.icons()])


class LibraryCatalog(Catalog[LibraryMatch]):
    """Every named item across some .excalidrawlib files."""

    def __init__(self, libraries: list[Path]):
        super().__init__([LibraryMatch(item) for path in libraries for item in LibraryFile(path).items if item.name])
