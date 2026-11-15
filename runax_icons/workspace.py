from dataclasses import dataclass
from pathlib import Path

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


@dataclass(frozen=True)
class IconMatch:
    pack: Pack
    label: str
    icon: Icon


class IconNotFound(WorkspaceError):
    pass


class AmbiguousIcon(WorkspaceError):
    def __init__(self, text: str, candidates: list[IconMatch]):
        super().__init__(f"{text!r} matches {len(candidates)} icons; use the full label or --pack")
        self.candidates = candidates


class IconCatalog:
    """Every icon across some packs, found by label or file name."""

    def __init__(self, packs: list[Pack]):
        self.matches = [IconMatch(pack, pack.label(icon), icon) for pack in packs for icon in pack.icons()]

    def search(self, text: str = "") -> list[IconMatch]:
        """Icons whose label or file name contains `text` (case-insensitive)."""
        needle = text.lower()
        return [
            m
            for m in self.matches
            if needle in m.label.lower() or needle in m.icon.path.stem.lower()
        ]

    def resolve(self, text: str) -> IconMatch:
        """The one icon `text` names: an exact label (case-insensitive), else a unique
        partial match."""
        found = self.search(text)
        candidates = [m for m in found if m.label.lower() == text.lower()] or found

        if not candidates:
            raise IconNotFound(f"no icon matches {text!r}; try `runax-icons search`")
        if len(candidates) > 1:
            raise AmbiguousIcon(text, candidates)
        return candidates[0]
