"""A pack's pack.yml as typed objects, validated on load."""

from dataclasses import dataclass, field
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

import yaml

from ..svg import Edit, Fill, Replace, ViewBox
from .imports import ArchiveImport, FileImport, ImportEntry, NamesTemplate

PACK_KEYS = {"title", "source", "license", "native_size", "publish", "import", "downloaded", "sources", "labels", "samples"}
IMPORT_KEYS = {"url", "into", "path", "note", "names", "fill", "viewBox", "replace"}
SOURCE_KEYS = {"files", "url", "note"}


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class SourceEntry:
    """A hand-made file (or files) in src/: drawn, cut out of a raster, or with no stable url."""

    files: str  # glob relative to src/
    url: str = ""
    note: str = ""

    def covers(self, path: str) -> bool:
        return fnmatch(path, self.files)


@dataclass(frozen=True)
class PackConfig:
    title: str
    source: str  # markdown, completes "N icons from ..." in the README
    license: str = ""  # markdown: the icons' license or terms
    native_size: bool = False  # show icons at their designed size (from the file name), not 64px
    publish: bool = False  # meant for libraries.excalidraw.com: CI enforces its guidelines
    imports: tuple[ImportEntry, ...] = ()
    downloaded: str = ""  # when the imports were last fetched
    sources: tuple[SourceEntry, ...] = ()
    labels: dict[str, str] = field(default_factory=dict)  # lowercased file name -> label
    samples: tuple[str, ...] = ()  # labels previewed in the README

    @classmethod
    def load(cls, path: Path) -> "PackConfig":
        try:
            return cls.parse(yaml.safe_load(path.read_text(encoding="utf-8")) or {})
        except ConfigError as error:
            raise ConfigError(f"{path}: {error}") from error

    @classmethod
    def parse(cls, data: dict[str, Any]) -> "PackConfig":
        _check_keys("pack.yml", data, PACK_KEYS, required={"title", "source"})
        return cls(
            title=data["title"],
            source=data["source"],
            license=data.get("license", ""),
            native_size=bool(data.get("native_size", False)),
            publish=bool(data.get("publish", False)),
            imports=tuple(_parse_import(entry) for entry in data.get("import") or []),
            downloaded=str(data.get("downloaded", "")),  # YAML reads dates as date
            sources=tuple(_parse_source(entry) for entry in data.get("sources") or []),
            labels=dict(data.get("labels") or {}),
            samples=tuple(data.get("samples") or []),
        )


def _parse_import(entry: dict[str, Any]) -> ImportEntry:
    _check_keys("import entry", entry, IMPORT_KEYS, required={"url"})
    into, note = entry.get("into", ""), entry.get("note", "")

    # An .svg target is one file; anything else is a folder an archive fills.
    if not into.endswith(".svg"):
        extra = {"names", "fill", "viewBox", "replace"} & entry.keys()
        if extra:
            raise ConfigError(f"{entry['url']}: {', '.join(sorted(extra))} only apply to .svg targets")
        return ArchiveImport(url=entry["url"], into=into, path=entry.get("path"), note=note)

    if "path" in entry:
        raise ConfigError(f"{entry['url']}: `path` only applies to archives")

    edits = _parse_edits(entry)
    names = entry.get("names")
    if names is None:
        return FileImport(url=entry["url"], into=into, edits=edits, note=note)

    pairs = dict(names) if isinstance(names, dict) else {name: name for name in names}
    return NamesTemplate(url=entry["url"], into=into, names=pairs, edits=edits, note=note)


def _parse_edits(entry: dict[str, Any]) -> tuple[Edit, ...]:
    """In the order they're applied: replace, then fill, then viewBox."""
    edits: list[Edit] = [Replace(old, new) for old, new in entry.get("replace", [])]
    if "fill" in entry:
        edits.append(Fill(entry["fill"]))
    if "viewBox" in entry:
        edits.append(ViewBox(entry["viewBox"]))
    return tuple(edits)


def _parse_source(entry: dict[str, Any]) -> SourceEntry:
    _check_keys("sources entry", entry, SOURCE_KEYS, required={"files"})
    return SourceEntry(files=entry["files"], url=entry.get("url", ""), note=entry.get("note", ""))


def _check_keys(what: str, data: Any, allowed: set[str], required: set[str]) -> None:
    if not isinstance(data, dict):
        raise ConfigError(f"{what} must be a mapping, got {data!r}")

    unknown = data.keys() - allowed
    if unknown:
        raise ConfigError(f"unknown keys in {what}: {', '.join(sorted(unknown))}")

    missing = required - data.keys()
    if missing:
        raise ConfigError(f"{what} is missing: {', '.join(sorted(missing))}")
