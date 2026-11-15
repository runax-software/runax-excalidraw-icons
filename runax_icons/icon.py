import base64
import re
import uuid
from dataclasses import dataclass
from functools import cached_property
from pathlib import PurePosixPath

from .svg import SvgDocument

# Stable namespace so the same SVG content always gets the same fileId across runs.
FILE_ID_NAMESPACE = uuid.UUID("6f1c3c3e-4f0a-4c39-9a51-0d2b1f3e8a77")

PREFIX_RE = re.compile(r"^(?:Arch(?:-Category)?_|Res_|\d+\s*-icon-service-)", re.IGNORECASE)
SIZE_SUFFIX_RE = re.compile(r"[_-](\d{2,3})(?:@\dx)?(?=(?:[_-](?:Light|Dark))?$)")  # _48, _48_Dark
SIZE_DIR_RE = re.compile(r"^\d{2,3}$")
LIGHT_RE = re.compile(r"[_-]Light$", re.IGNORECASE)


@dataclass(frozen=True)
class Icon:
    """One SVG file: its name (label, size variant) from the path, its image from the content."""

    path: PurePosixPath  # relative to the package root (zip or folder)
    data: bytes

    @cached_property
    def document(self) -> SvgDocument:
        return SvgDocument(self.data)

    @property
    def size(self) -> int:
        """Resolution from the filename suffix (_64) or size folder (64/); 0 if neither."""
        match = SIZE_SUFFIX_RE.search(self.path.stem)
        if match:
            return int(match.group(1))

        for part in reversed(self.path.parent.parts):
            if SIZE_DIR_RE.match(part):
                return int(part)

        return 0

    @property
    def key(self) -> str:
        """Identity regardless of which resolution variant this is."""
        return re.sub(r"\s+", "", SIZE_SUFFIX_RE.sub("", self.path.stem)).lower()

    @property
    def rank(self) -> tuple[int, bool]:
        """Higher wins among variants of the same icon: largest size, unlabeled over labeled."""
        return self.size, "unlabeled" in self.path.parts

    def label(self, overrides: dict[str, str]) -> str:
        """Display name; `overrides` maps lowercased file names (without size suffix) to labels."""
        name = SIZE_SUFFIX_RE.sub("", self.path.stem)
        if name.lower() in overrides:
            return overrides[name.lower()]

        name = LIGHT_RE.sub("", name)  # its white `_Dark` twin is skipped, so the suffix is noise
        name = PREFIX_RE.sub("", name)
        words = [w for w in re.split(r"[-_\s]+", name) if w]

        # Capitalize the first letter only, so acronyms like EC2 / IoT / VPN survive.
        return " ".join(w[:1].upper() + w[1:] for w in words)

    @property
    def aspect(self) -> float:
        return self.document.aspect

    @property
    def is_white_only(self) -> bool:
        return self.document.is_white_only

    @cached_property
    def base64(self) -> str:
        return base64.b64encode(self.document.rendered().data).decode("ascii")

    @property
    def file_id(self) -> str:
        return uuid.uuid5(FILE_ID_NAMESPACE, self.base64).hex

    @property
    def data_url(self) -> str:
        return "data:image/svg+xml;base64," + self.base64
