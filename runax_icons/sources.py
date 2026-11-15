import tarfile
import zipfile
from abc import ABC, abstractmethod
from collections.abc import Iterator
from fnmatch import fnmatch
from pathlib import Path, PurePosixPath

from .icon import Icon


class IconSource(ABC):
    """Every SVG in a package, as Icons with paths relative to the package root.

    `root` is an optional glob for a folder inside the package (e.g. "community-*/icons"):
    only SVGs under a matching folder are read, with paths relative to it.
    """

    def __init__(self, path: Path, root: str | None = None):
        self.path = path
        self.root = root

    @staticmethod
    def open(path: Path, root: str | None = None) -> "IconSource":
        if path.is_dir():
            return FolderSource(path, root)
        if zipfile.is_zipfile(path):
            return ZipSource(path, root)
        if tarfile.is_tarfile(path):
            return TarSource(path, root)

        raise ValueError(f"{path}: not a folder, zip or tar archive")

    @abstractmethod
    def __iter__(self) -> Iterator[Icon]: ...

    def _relative(self, path: PurePosixPath) -> PurePosixPath | None:
        """`path` relative to the root folder, or None if it's outside it or not an icon."""
        # __MACOSX/._*.svg entries are Finder metadata, not icons.
        if (
            "__MACOSX" in path.parts
            or path.name.startswith("._")
            or path.suffix.lower() != ".svg"
        ):
            return None
        if not self.root:
            return path

        depth = len(PurePosixPath(self.root).parts)
        if not fnmatch(PurePosixPath(*path.parts[:depth]).as_posix(), self.root):
            return None

        return PurePosixPath(*path.parts[depth:])


class FolderSource(IconSource):
    def __iter__(self) -> Iterator[Icon]:
        for path in sorted(self.path.rglob("*.svg")):
            relative = self._relative(PurePosixPath(path.relative_to(self.path).as_posix()))
            if relative:
                yield Icon(relative, path.read_bytes())


class ZipSource(IconSource):
    def __iter__(self) -> Iterator[Icon]:
        with zipfile.ZipFile(self.path) as archive:
            for info in archive.infolist():
                relative = self._relative(PurePosixPath(info.filename))
                if relative:
                    yield Icon(relative, archive.read(info))


class TarSource(IconSource):
    def __iter__(self) -> Iterator[Icon]:
        with tarfile.open(self.path) as archive:
            for member in archive:
                relative = self._relative(PurePosixPath(member.name))
                file = archive.extractfile(member) if member.isfile() and relative else None
                if relative and file:
                    yield Icon(relative, file.read())
