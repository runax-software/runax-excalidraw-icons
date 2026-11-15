"""SVG files: reading their geometry and editing them."""

from .document import SvgDocument, SvgError
from .edits import Edit, EditError, Fill, Replace, ViewBox

__all__ = ["Edit", "EditError", "Fill", "Replace", "SvgDocument", "SvgError", "ViewBox"]
