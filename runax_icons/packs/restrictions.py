"""What a pack's icons may be put through: `forbid:` in pack.yml, on the pack or on an entry."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ConfigError(Exception):
    pass


class ForbiddenError(ConfigError):
    """An operation the pack's `forbid:` rules out, usually because of its icons' terms."""


class Operation(StrEnum):
    """What a pack can be put through, and so what its `forbid:` can rule out."""

    EDIT = "edit"  # declared edits on imported files: fill, viewBox, replace
    NATIVE = "native"  # redrawing icons as native Excalidraw shapes (approximates their shape)
    PUBLISH = "publish"  # `publish: true`: a native library for libraries.excalidraw.com


@dataclass(frozen=True)
class Restrictions:
    """The operations a pack forbids, each with the reason (shown in errors and the README)."""

    forbidden: dict[Operation, str] = field(default_factory=dict)

    @classmethod
    def parse(cls, data: Any) -> "Restrictions":
        if not isinstance(data, dict):
            raise ConfigError(f"forbid must map operations to reasons, got {data!r}")

        unknown = set(data) - {op.value for op in Operation}
        if unknown:
            known = ", ".join(op.value for op in Operation)
            raise ConfigError(f"unknown operations in forbid: {', '.join(sorted(unknown))} (known: {known})")

        return cls({Operation(op): str(reason) for op, reason in data.items()})

    def __bool__(self) -> bool:
        return bool(self.forbidden)

    def __or__(self, other: "Restrictions") -> "Restrictions":
        """Both sets of restrictions (a file is bound by its pack's and its entry's)."""
        return Restrictions({**other.forbidden, **self.forbidden})

    def allows(self, operation: Operation) -> bool:
        return operation not in self.forbidden

    def require(self, operation: Operation, what: str) -> None:
        """Raise ForbiddenError, with the pack's reason, if `operation` is forbidden."""
        if not self.allows(operation):
            raise ForbiddenError(f"{what}: `{operation}` is forbidden here: {self.forbidden[operation]}")
