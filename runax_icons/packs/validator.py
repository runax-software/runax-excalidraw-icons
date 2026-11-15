from dataclasses import dataclass

from ..icon import Icon
from .imports import FileImport
from .pack import Pack


@dataclass(frozen=True)
class Problem:
    pack: str
    message: str

    def __str__(self) -> str:
        return f"[{self.pack}] {self.message}"


class Validator:
    """What's wrong with a pack: icons nothing covers, `sources` entries that match no icon,
    imported files missing from src/, and README samples that aren't labels."""

    def __init__(self, pack: Pack, icons: list[Icon] | None = None):
        self.pack = pack
        self.icons = icons if icons is not None else pack.icons()

    def problems(self) -> list[Problem]:
        checks = [self._unsourced, self._unused_sources, self._missing_imports, self._absent_samples]
        return [Problem(self.pack.name, message) for check in checks if (message := check())]

    def _unsourced(self) -> str | None:
        paths = [icon.path.as_posix() for icon in self.icons if not self.pack.source_of(icon)]
        return f"icons without a source: {', '.join(paths)}" if paths else None

    def _unused_sources(self) -> str | None:
        used = {id(self.pack.source_of(icon)) for icon in self.icons}
        unused = [s.files for s in self.pack.config.sources if id(s) not in used]
        return f"sources matching no icon: {', '.join(unused)}" if unused else None

    def _missing_imports(self) -> str | None:
        missing = [
            t.into
            for t in self.pack.import_targets
            if isinstance(t, FileImport) and not (self.pack.src_dir / t.into).exists()
        ]
        if not missing:
            return None
        return f"not in src/, run `runax-icons import {self.pack.name}`: {', '.join(missing)}"

    def _absent_samples(self) -> str | None:
        labels = {self.pack.label(icon) for icon in self.icons}
        absent = [s for s in self.pack.config.samples if s not in labels]
        return f"README samples not found: {', '.join(absent)}" if absent else None
