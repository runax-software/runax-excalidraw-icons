"""Declared edits an `import:` entry applies to a downloaded file."""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass

from .document import SvgDocument

# Attribute values may be single- or double-quoted.
BLACK_RE = re.compile(r'\b(fill|stroke)=(["\'])(?:#000|#000000|black|currentColor)\2', re.IGNORECASE)
VIEWBOX_ATTR_RE = re.compile(r'\sviewBox=(?:"[^"]*"|\'[^\']*\')')
COLOR_ATTR_RE = re.compile(r'\scolor=(?:"[^"]*"|\'[^\']*\')')


class EditError(Exception):
    pass


class Edit(ABC):
    @abstractmethod
    def apply(self, document: SvgDocument) -> SvgDocument: ...

    @abstractmethod
    def describe(self) -> str:
        """The edit in a few words, for a pack README's Sources table."""


@dataclass(frozen=True)
class Replace(Edit):
    """Swap a piece of text, which must be present (a silent no-op would hide an upstream change)."""

    old: str
    new: str

    def apply(self, document: SvgDocument) -> SvgDocument:
        if self.old not in document.text:
            raise EditError(f"replace text not found: {self.old!r}")
        return document.with_text(document.text.replace(self.old, self.new))

    def describe(self) -> str:
        return "text replaced"


@dataclass(frozen=True)
class Fill(Edit):
    """Paint a single-color icon: black and currentColor become `color`, and the root gets it
    as its color and (unless it sets one) default fill."""

    color: str

    def apply(self, document: SvgDocument) -> SvgDocument:
        document = document.with_text(BLACK_RE.sub(rf'\1="{self.color}"', document.text))
        tag = document.root_tag
        root = COLOR_ATTR_RE.sub("", tag)[:-1] + f' color="{self.color}"'
        if not re.search(r"\sfill=", tag):
            root += f' fill="{self.color}"'

        return document.with_root_tag(root + ">")

    def describe(self) -> str:
        return f"filled {self.color}"


@dataclass(frozen=True)
class ViewBox(Edit):
    """Crop to `box`, e.g. to drop a wordmark. Width and height go, so the build sizes the
    icon from the viewBox."""

    box: str

    def apply(self, document: SvgDocument) -> SvgDocument:
        root = document.without_size().root_tag
        if VIEWBOX_ATTR_RE.search(root):
            root = VIEWBOX_ATTR_RE.sub(f' viewBox="{self.box}"', root)
        else:
            root = root[:-1] + f' viewBox="{self.box}">'

        return document.with_root_tag(root)

    def describe(self) -> str:
        return "viewBox cropped"
