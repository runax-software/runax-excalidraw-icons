import tarfile
import zipfile
from fnmatch import fnmatch
from pathlib import PurePosixPath

from builder.icon import Icon


class IconSource:
    """Every SVG in a package, as Icons with paths relative to the package root.

    `root` is an optional glob for a folder inside the package (e.g. "community-*/icons"):
    only SVGs under a matching folder are read, with paths relative to it.
    """

    def __init__(self, path, root=None):
        self.path = path
        self.root = root

    @staticmethod
    def open(path, root=None):
        if path.is_dir():
            return FolderSource(path, root)
        if zipfile.is_zipfile(path):
            return ZipSource(path, root)
        if tarfile.is_tarfile(path):
            return TarSource(path, root)

        raise ValueError(f"{path}: not a folder, zip or tar archive")

    def __iter__(self):
        raise NotImplementedError

    def _relative(self, path):
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
    def __iter__(self):
        for path in sorted(self.path.rglob("*.svg")):
            relative = self._relative(PurePosixPath(path.relative_to(self.path).as_posix()))
            if relative:
                yield Icon(relative, path.read_bytes())


class ZipSource(IconSource):
    def __iter__(self):
        with zipfile.ZipFile(self.path) as archive:
            for info in archive.infolist():
                relative = self._relative(PurePosixPath(info.filename))
                if relative:
                    yield Icon(relative, archive.read(info))


class TarSource(IconSource):
    def __iter__(self):
        with tarfile.open(self.path) as archive:
            for member in archive:
                relative = member.isfile() and self._relative(PurePosixPath(member.name))
                if relative:
                    yield Icon(relative, archive.extractfile(member).read())
