"""The libraries.excalidraw.com submission guidelines, as checks on an .excalidrawlib.

https://github.com/excalidraw/excalidraw-libraries#guidelines. Rules that need judgment (is it
useful to others? is it copied from another library?) are listed, not checked.
"""

import json
import unicodedata
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

BASIC_SHAPES = {"rectangle", "ellipse", "diamond", "arrow", "line"}
MIN_ITEMS = 3

MANUAL_RULES = [
    "1. Useful to others, not only for a personal use case",
    "3. Not republished from other libraries without significant changes",
]


@dataclass(frozen=True)
class Finding:
    rule: str
    message: str

    def __str__(self) -> str:
        return f"{self.rule}: {self.message}"


class LibraryFile:
    """An .excalidrawlib's items, read for checking."""

    def __init__(self, path: Path):
        self.path = path
        data = json.loads(path.read_text(encoding="utf-8"))
        self.items: list[dict[str, Any]] = data.get("libraryItems", [])

    @staticmethod
    def elements(item: dict[str, Any]) -> list[dict[str, Any]]:
        return [e for e in item.get("elements", []) if not e.get("isDeleted")]


class Rule(ABC):
    name: str

    @abstractmethod
    def check(self, library: LibraryFile) -> list[str]:
        """Messages describing violations; empty when the library follows the rule."""

    def findings(self, library: LibraryFile) -> list[Finding]:
        return [Finding(self.name, message) for message in self.check(library)]


class NotTrivial(Rule):
    name = "2. Items aren't easy to create directly"

    def check(self, library: LibraryFile) -> list[str]:
        return [
            f"{item.get('name') or 'unnamed item'}: only a basic shape"
            for item in library.items
            if (elements := library.elements(item))
            and len(elements) <= 2
            and all(e["type"] in BASIC_SHAPES for e in elements)
        ]


class EnglishOnly(Rule):
    name = "4. English only"

    def check(self, library: LibraryFile) -> list[str]:
        texts = [(item.get("name", ""), item) for item in library.items] + [
            (e.get("originalText", e.get("text", "")), item)
            for item in library.items
            for e in library.elements(item)
            if e["type"] == "text"
        ]
        return [
            f"{item.get('name') or 'unnamed item'}: non-Latin text {text!r}"
            for text, item in texts
            if not _latin(text)
        ]


class StandsAlone(Rule):
    name = "5. Each item is usable on its own"

    def check(self, library: LibraryFile) -> list[str]:
        problems = []
        for item in library.items:
            name = item.get("name") or "unnamed item"
            if not library.elements(item):
                problems.append(f"{name}: empty")
            elif not item.get("name"):
                problems.append("an item has no name")
        return problems


class EnoughItems(Rule):
    name = f"6. At least {MIN_ITEMS} related items"

    def check(self, library: LibraryFile) -> list[str]:
        count = len(library.items)
        return [] if count >= MIN_ITEMS else [f"{count} items"]


class Grouped(Rule):
    name = "7. Multi-element items are grouped"

    def check(self, library: LibraryFile) -> list[str]:
        problems = []
        for item in library.items:
            elements = library.elements(item)
            if len(elements) > 1 and not set.intersection(*(set(e.get("groupIds", [])) for e in elements)):
                problems.append(f"{item.get('name') or 'unnamed item'}: elements not grouped")
        return problems


class NoImages(Rule):
    """Not in the written guidelines, but libraries.excalidraw.com stores only the library
    file, which has no place for image data: an image item installs as an empty box."""

    name = "Items render without images"

    def check(self, library: LibraryFile) -> list[str]:
        with_images = [
            item.get("name") or "unnamed item"
            for item in library.items
            if any(e["type"] == "image" for e in library.elements(item))
        ]
        if not with_images:
            return []
        return [f"{len(with_images)} of {len(library.items)} items are images, e.g. {', '.join(with_images[:3])}"]


RULES: list[Rule] = [NotTrivial(), EnglishOnly(), StandsAlone(), EnoughItems(), Grouped(), NoImages()]


class Guidelines:
    """Checks a library against every automatable rule."""

    def __init__(self, rules: list[Rule] | None = None):
        self.rules = rules if rules is not None else RULES

    def check(self, library: LibraryFile) -> list[Finding]:
        return [finding for rule in self.rules for finding in rule.findings(library)]


def _latin(text: str) -> bool:
    """Only Latin-script letters (accents allowed), digits, punctuation and symbols."""
    return all(
        not ch.isalpha() or ch.isascii() or "LATIN" in unicodedata.name(ch, "")
        for ch in text
    )
