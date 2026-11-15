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
WEBP_MAGIC = (b"RIFF", b"WEBP")  # bytes 0-4 and 8-12
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
    def from_raster(cls, data: bytes, mime: str, width: int, height: int) -> "SvgDocument":
        """An SVG showing a raster image at its own size."""
        encoded = base64.b64encode(data).decode("ascii")
        return cls.from_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">'
            f'<image width="{width}" height="{height}" href="data:{mime};base64,{encoded}"/></svg>'
        )

    @classmethod
    def from_png(cls, data: bytes) -> "SvgDocument":
        width, height = struct.unpack(">II", data[16:24])  # the IHDR chunk follows the magic
        return cls.from_raster(data, "image/png", width, height)

    @classmethod
    def from_webp(cls, data: bytes) -> "SvgDocument":
        return cls.from_raster(data, "image/webp", *_webp_size(data))

    @classmethod
    def from_download(cls, data: bytes) -> "SvgDocument":
        """A downloaded SVG, or a PNG or WebP (recognized by content, not name) wrapped in one.
        Anything else must be an SVG: its root tag is checked, so an error page or an
        unexpected format fails here instead of being written to src/."""
        if data.startswith(PNG_MAGIC):
            return cls.from_png(data)
        if data[:4] == WEBP_MAGIC[0] and data[8:12] == WEBP_MAGIC[1]:
            return cls.from_webp(data)

        document = cls(data)
        document.root_tag  # raises SvgError if this isn't an SVG
        return document

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


def _webp_size(data: bytes) -> tuple[int, int]:
    """Width and height from a WebP's first chunk (lossy VP8, lossless VP8L or extended VP8X)."""
    chunk = data[12:16]
    if chunk == b"VP8 ":
        width, height = struct.unpack("<HH", data[26:30])
        return width & 0x3FFF, height & 0x3FFF
    if chunk == b"VP8L":
        bits = int.from_bytes(data[21:25], "little")
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    if chunk == b"VP8X":
        return int.from_bytes(data[24:27], "little") + 1, int.from_bytes(data[27:30], "little") + 1

    raise SvgError(f"unsupported WebP chunk {chunk!r}")
