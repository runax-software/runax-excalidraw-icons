import base64
import re
import struct
from functools import cached_property

ROOT_TAG_RE = re.compile(r"<svg\b[^>]*>", re.IGNORECASE)
VIEWBOX_RE = re.compile(r'\bviewBox\s*=\s*"([^"]+)"', re.IGNORECASE)
DIMENSION_RE = r'\b{}\s*=\s*"\s*([\d.]+)(?:px)?\s*"'
ABSOLUTE_SIZE_RE = r'\s{}\s*=\s*"\s*[\d.]+\s*(?:px|pt|mm|cm|in)?\s*"'
SIZE_ATTR_RE = re.compile(r'\s(?:width|height)\s*=\s*"[^"]*"')
COLOR_RE = re.compile(
    r'(?:fill|stroke|stop-color)\s*[=:]\s*"?\s*(#[0-9a-f]{3,8}|[a-z]+)', re.IGNORECASE
)
SHAPE_RE = re.compile(
    r"<(?:path|rect|circle|ellipse|polygon|polyline|line|text)\b([^>]*)>", re.IGNORECASE
)
GROUP_FILL_RE = re.compile(
    r'<(?:svg|g)\b[^>]*\bfill\s*[=:]\s*"?\s*(?!none)[#a-z]', re.IGNORECASE
)
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
WHITE = {"#fff", "#ffffff", "white"}
NO_PAINT = {"none", "transparent", "currentcolor", "inherit"}
RENDER_SIZE = 256  # longer side given to SVGs that only have a viewBox


class SvgError(Exception):
    pass


class SvgDocument:
    """An SVG file's bytes, with what the build needs to know about its root <svg> tag.

    Documents are immutable: edits return a new document, so the original bytes stay
    available and unedited files are written back byte for byte.
    """

    def __init__(self, data: bytes):
        self.data = data

    @classmethod
    def from_text(cls, text: str) -> "SvgDocument":
        return cls(text.encode("utf-8"))

    @classmethod
    def from_png(cls, data: bytes) -> "SvgDocument":
        """An SVG showing the PNG at its own size."""
        width, height = struct.unpack(">II", data[16:24])  # the IHDR chunk follows the magic
        encoded = base64.b64encode(data).decode("ascii")

        return cls.from_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">'
            f'<image width="{width}" height="{height}" href="data:image/png;base64,{encoded}"/></svg>'
        )

    @classmethod
    def from_download(cls, data: bytes) -> "SvgDocument":
        """A downloaded SVG, or a PNG wrapped in one."""
        return cls.from_png(data) if data.startswith(PNG_MAGIC) else cls(data)

    @cached_property
    def text(self) -> str:
        return self.data.decode("utf-8", errors="ignore")

    @cached_property
    def _root_match(self) -> re.Match[str] | None:
        return ROOT_TAG_RE.search(self.text)

    @property
    def has_root(self) -> bool:
        return self._root_match is not None

    @property
    def root_tag(self) -> str:
        """The root <svg ...> tag; SvgError if the file has none (an error page, not an SVG)."""
        if self._root_match is None:
            raise SvgError("no <svg> root tag")
        return self._root_match.group()

    def with_root_tag(self, tag: str) -> "SvgDocument":
        """This document with its root <svg> tag replaced by `tag`."""
        return SvgDocument.from_text(self.text.replace(self.root_tag, tag, 1))

    def with_text(self, text: str) -> "SvgDocument":
        return SvgDocument.from_text(text)

    @cached_property
    def aspect(self) -> float:
        """Width / height of the root <svg>, from its viewBox or width/height; 1 if unknown."""
        if not self.has_root:
            return 1

        viewbox = VIEWBOX_RE.search(self.root_tag)
        if viewbox:
            parts = re.split(r"[\s,]+", viewbox.group(1).strip())
            if len(parts) == 4 and float(parts[3]) > 0:
                return float(parts[2]) / float(parts[3])

        width = re.search(DIMENSION_RE.format("width"), self.root_tag)
        height = re.search(DIMENSION_RE.format("height"), self.root_tag)
        if width and height and float(height.group(1)) > 0:
            return float(width.group(1)) / float(height.group(1))

        return 1

    @cached_property
    def has_absolute_size(self) -> bool:
        return self.has_root and all(
            re.search(ABSOLUTE_SIZE_RE.format(attr), self.root_tag)
            for attr in ("width", "height")
        )

    @cached_property
    def is_white_only(self) -> bool:
        """Painted only in white: invisible on a white canvas (AWS `_Dark` variants)."""
        painted = {c.lower() for c in COLOR_RE.findall(self.text)} - NO_PAINT
        if not painted or not painted <= WHITE:
            return False

        # A shape without its own fill renders black unless a parent group sets one.
        unfilled = any("fill" not in attrs for attrs in SHAPE_RE.findall(self.text))
        return not unfilled or bool(GROUP_FILL_RE.search(self.text))

    def without_size(self) -> "SvgDocument":
        """The root tag without width and height, so its viewBox decides the shape."""
        return self.with_root_tag(SIZE_ATTR_RE.sub("", self.root_tag))

    def rendered(self) -> "SvgDocument":
        """The document with an absolute width and height on its root.

        Browsers load an SVG without one (only a viewBox, or 1em / 100%) at a default
        300x150, which Excalidraw then stretches to the element, distorting non-square icons.
        """
        if not self.has_root or self.has_absolute_size:
            return self

        width = round(RENDER_SIZE * min(1, self.aspect), 2)
        height = round(RENDER_SIZE * min(1, 1 / self.aspect), 2)
        sized = SIZE_ATTR_RE.sub("", self.root_tag)
        sized = re.sub(r"<svg\b", f'<svg width="{width}" height="{height}"', sized, count=1)
        return self.with_root_tag(sized)
