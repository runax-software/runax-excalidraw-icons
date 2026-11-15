import base64
import re
import uuid
from dataclasses import dataclass
from functools import cached_property
from pathlib import PurePosixPath

# Stable namespace so the same SVG content always gets the same fileId across runs.
FILE_ID_NAMESPACE = uuid.UUID("6f1c3c3e-4f0a-4c39-9a51-0d2b1f3e8a77")

PREFIX_RE = re.compile(
    r"^(?:Arch(?:-Category)?_|Res_|\d+\s*-icon-service-)", re.IGNORECASE
)
SIZE_SUFFIX_RE = re.compile(
    r"[_-](\d{2,3})(?:@\dx)?(?=(?:[_-](?:Light|Dark))?$)"
)  # _48, _48_Dark
SIZE_DIR_RE = re.compile(r"^\d{2,3}$")
LIGHT_RE = re.compile(r"[_-]Light$", re.IGNORECASE)
COLOR_RE = re.compile(
    r'(?:fill|stroke|stop-color)\s*[=:]\s*"?\s*(#[0-9a-f]{3,8}|[a-z]+)', re.IGNORECASE
)
SHAPE_RE = re.compile(
    r"<(?:path|rect|circle|ellipse|polygon|polyline|line|text)\b([^>]*)>", re.IGNORECASE
)
GROUP_FILL_RE = re.compile(
    r'<(?:svg|g)\b[^>]*\bfill\s*[=:]\s*"?\s*(?!none)[#a-z]', re.IGNORECASE
)
SVG_TAG_RE = re.compile(r"<svg\b[^>]*>", re.IGNORECASE)
VIEWBOX_RE = re.compile(r'\bviewBox\s*=\s*"([^"]+)"', re.IGNORECASE)
DIMENSION_RE = r'\b{}\s*=\s*"\s*([\d.]+)(?:px)?\s*"'
ABSOLUTE_SIZE_RE = r'\s{}\s*=\s*"\s*[\d.]+\s*(?:px|pt|mm|cm|in)?\s*"'
SIZE_ATTR_RE = re.compile(r'\s(?:width|height)\s*=\s*"[^"]*"')
RENDER_SIZE = 256  # longer side given to SVGs that only have a viewBox
WHITE = {"#fff", "#ffffff", "white"}
NO_PAINT = {"none", "transparent", "currentcolor", "inherit"}


@dataclass(frozen=True)
class Icon:
    """One SVG file and everything derived from its path and content."""

    path: PurePosixPath  # relative to the package root (zip or folder)
    svg: bytes

    @property
    def size(self):
        """Resolution from the filename suffix (_64) or size folder (64/)."""
        m = SIZE_SUFFIX_RE.search(self.path.stem)
        if m:
            return int(m.group(1))

        for part in reversed(self.path.parent.parts):
            if SIZE_DIR_RE.match(part):
                return int(part)

        return 0

    @property
    def key(self):
        """Identity regardless of which resolution variant this is."""
        return re.sub(r"\s+", "", SIZE_SUFFIX_RE.sub("", self.path.stem)).lower()

    @property
    def rank(self):
        """Higher wins among variants of the same icon: largest size, unlabeled over labeled."""
        return self.size, "unlabeled" in self.path.parts

    @cached_property
    def is_white_only(self):
        text = self.svg.decode("utf-8", errors="ignore")
        painted = {c.lower() for c in COLOR_RE.findall(text)} - NO_PAINT

        if not painted or not painted <= WHITE:
            return False

        # A shape without its own fill renders black unless a parent group sets one.
        unfilled = any("fill" not in attrs for attrs in SHAPE_RE.findall(text))
        return not unfilled or bool(GROUP_FILL_RE.search(text))

    @cached_property
    def aspect(self):
        """Width / height of the root <svg>, from its viewBox or width/height; 1 if unknown."""
        tag = SVG_TAG_RE.search(self.svg.decode("utf-8", errors="ignore"))
        if not tag:
            return 1

        viewbox = VIEWBOX_RE.search(tag.group())
        if viewbox:
            parts = re.split(r"[\s,]+", viewbox.group(1).strip())
            if len(parts) == 4 and float(parts[3]) > 0:
                return float(parts[2]) / float(parts[3])

        width = re.search(DIMENSION_RE.format("width"), tag.group())
        height = re.search(DIMENSION_RE.format("height"), tag.group())
        if width and height and float(height.group(1)) > 0:
            return float(width.group(1)) / float(height.group(1))

        return 1

    @cached_property
    def rendered_svg(self):
        """The SVG with an absolute width and height on its root.

        Browsers load an SVG without one (only a viewBox, or 1em / 100%) at a default
        300x150, which Excalidraw then stretches to the element, distorting non-square icons.
        """
        text = self.svg.decode("utf-8", errors="ignore")
        tag = SVG_TAG_RE.search(text)
        if not tag or all(
            re.search(ABSOLUTE_SIZE_RE.format(attr), tag.group())
            for attr in ("width", "height")
        ):
            return self.svg

        width = round(RENDER_SIZE * min(1, self.aspect), 2)
        height = round(RENDER_SIZE * min(1, 1 / self.aspect), 2)
        sized = SIZE_ATTR_RE.sub("", tag.group())
        sized = re.sub(
            r"<svg\b", f'<svg width="{width}" height="{height}"', sized, count=1
        )
        return text.replace(tag.group(), sized, 1).encode("utf-8")

    @cached_property
    def base64(self):
        return base64.b64encode(self.rendered_svg).decode("ascii")

    @property
    def file_id(self):
        return uuid.uuid5(FILE_ID_NAMESPACE, self.base64).hex

    @property
    def data_url(self):
        return "data:image/svg+xml;base64," + self.base64

    def label(self, overrides):
        """Display name; `overrides` maps lowercased file names (without size suffix) to labels."""
        name = SIZE_SUFFIX_RE.sub("", self.path.stem)
        if name.lower() in overrides:
            return overrides[name.lower()]

        name = LIGHT_RE.sub(
            "", name
        )  # its white `_Dark` twin is skipped, so the suffix is noise

        name = PREFIX_RE.sub("", name)
        words = [w for w in re.split(r"[-_\s]+", name) if w]

        # Capitalize the first letter only, so acronyms like EC2 / IoT / VPN survive.
        return " ".join(w[:1].upper() + w[1:] for w in words)
