import zipfile
from pathlib import PurePosixPath

from builder.icon import Icon


class IconSource:
    """Every SVG in a downloaded package, as Icons with paths relative to the package root."""

    def __init__(self, path):
        self.path = path

    @staticmethod
    def open(path):
        return FolderSource(path) if path.is_dir() else ZipSource(path)

    def __iter__(self):
        raise NotImplementedError


class FolderSource(IconSource):
    def __iter__(self):
        for path in sorted(self.path.rglob("*.svg")):
            yield Icon(
                PurePosixPath(path.relative_to(self.path).as_posix()), path.read_bytes()
            )


class ZipSource(IconSource):
    def __iter__(self):
        with zipfile.ZipFile(self.path) as archive:
            for info in archive.infolist():
                path = PurePosixPath(info.filename)
                # __MACOSX/._*.svg entries are Finder metadata, not icons.
                if (
                    "__MACOSX" in path.parts
                    or path.name.startswith("._")
                    or path.suffix.lower() != ".svg"
                ):
                    continue
                yield Icon(path, archive.read(info))
