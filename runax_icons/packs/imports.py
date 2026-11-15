"""`import:` entries: where a pack's files come from upstream, and how they're written to src/."""

import shutil
import tarfile
import zipfile
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from ..icon import Icon
from ..sources import IconSource
from ..svg import Edit, EditError, SvgDocument, SvgError
from .restrictions import Restrictions


class UpstreamError(Exception):
    pass


class ImportEntry(ABC):
    """One `import:` entry as written in pack.yml."""

    url: str
    note: str
    edits: tuple[Edit, ...] = ()  # declared edits; only single-file imports have any
    forbid: Restrictions = Restrictions()  # on top of the pack's

    @abstractmethod
    def targets(self) -> list["ImportTarget"]:
        """The concrete imports this entry stands for."""

    @property
    @abstractmethod
    def files(self) -> str:
        """Glob of the files it writes, relative to src/, for the README."""

    def notes(self) -> list[str]:
        """What a reader of the README should know about it."""
        notes = [self.note] if self.note else []
        if self.forbid:
            notes.append("forbids " + ", ".join(f"`{op}`" for op in self.forbid.forbidden))
        return notes


class ImportTarget(ImportEntry):
    """An import that writes to one place in src/."""

    def targets(self) -> list["ImportTarget"]:
        return [self]

    @abstractmethod
    def covers(self, path: str) -> bool:
        """Whether the file at `path` (relative to src/) comes from this import."""

    @abstractmethod
    def write(self, download: Path, src: Path) -> int:
        """Write the downloaded `download` into `src`; return how many icons it wrote."""


@dataclass(frozen=True)
class ArchiveImport(ImportTarget):
    """A zip or tar whose icons replace the folder src/<into>/ (all of src/ by default):
    the largest size of each icon under `path`, without white-only ones."""

    url: str
    into: str = ""
    path: str | None = None
    note: str = ""
    forbid: Restrictions = Restrictions()

    @property
    def files(self) -> str:
        return f"{self.into}/**" if self.into else "**"

    def notes(self) -> list[str]:
        notes = super().notes() + ["largest size of each icon, white-only ones skipped"]
        if self.path:
            notes.append(f"from `{self.path}` in the archive")
        return notes

    def covers(self, path: str) -> bool:
        return not self.into or path.startswith(self.into.rstrip("/") + "/")

    def write(self, download: Path, src: Path) -> int:
        if not (zipfile.is_zipfile(download) or tarfile.is_tarfile(download)):
            raise UpstreamError(f"{self.url} is not a zip or tar archive")

        icons = self.select(IconSource.open(download, self.path))
        if not icons:
            raise UpstreamError(f"no icons in {self.url} under {self.path!r}")

        target = src / self.into
        shutil.rmtree(target, ignore_errors=True)
        for icon in icons:
            path = target / icon.path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(icon.data)

        return len(icons)

    @staticmethod
    def select(source: IconSource) -> list[Icon]:
        """The best variant of each icon (see Icon.rank), minus white-only ones."""
        best: dict[str, Icon] = {}
        for icon in source:
            if icon.is_white_only:
                continue
            if icon.key not in best or icon.rank > best[icon.key].rank:
                best[icon.key] = icon

        return list(best.values())


@dataclass(frozen=True)
class FileImport(ImportTarget):
    """One SVG (or PNG, wrapped in an SVG) written to src/<into> after its edits."""

    url: str
    into: str
    edits: tuple[Edit, ...] = ()
    note: str = ""
    forbid: Restrictions = Restrictions()

    @property
    def files(self) -> str:
        return self.into

    def notes(self) -> list[str]:
        described = list(dict.fromkeys(edit.describe() for edit in self.edits))
        return super().notes() + described

    def covers(self, path: str) -> bool:
        return path == self.into

    def write(self, download: Path, src: Path) -> int:
        document = SvgDocument.from_download(download.read_bytes())
        try:
            for edit in self.edits:
                document = edit.apply(document)
        except (EditError, SvgError) as error:
            raise UpstreamError(f"{self.url}: {error}") from error

        target = src / self.into
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(document.data)
        return 1


@dataclass(frozen=True)
class NamesTemplate(ImportEntry):
    """Many files from one place: one FileImport per name, filling {name} and {src} (the
    upstream name, for a map of name -> src) in `url` and `into`."""

    url: str
    into: str
    names: dict[str, str]
    edits: tuple[Edit, ...] = ()
    note: str = ""
    forbid: Restrictions = Restrictions()

    @property
    def files(self) -> str:
        return self.into.format(name="*", src="*")

    def notes(self) -> list[str]:
        described = list(dict.fromkeys(edit.describe() for edit in self.edits))
        return super().notes() + described + [f"{len(self.names)} files"]

    def targets(self) -> list[ImportTarget]:
        return [
            FileImport(
                url=self.url.format(name=name, src=src),
                into=self.into.format(name=name, src=src),
                edits=self.edits,
                note=self.note,
                forbid=self.forbid,
            )
            for name, src in self.names.items()
        ]
