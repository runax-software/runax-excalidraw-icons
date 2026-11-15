"""Edits an `import:` entry applies to a downloaded file before it goes into src/."""

import base64
import re
import struct

SVG_TAG_RE = re.compile(r"<svg\b[^>]*>", re.IGNORECASE)
SIZE_ATTR_RE = re.compile(r'\s(?:width|height)\s*=\s*"[^"]*"')
BLACK_RE = re.compile(r'\b(fill|stroke)="(?:#000|#000000|black|currentColor)"', re.IGNORECASE)
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def apply(data, entry):
    """`data` (SVG or PNG bytes) as an SVG, with the entry's edits applied in order:
    PNGs are wrapped in an SVG, then `replace`, `fill` and `viewBox`."""
    text = wrap_png(data) if data.startswith(PNG_MAGIC) else data.decode("utf-8")

    for old, new in entry.get("replace", []):
        if old not in text:
            raise ValueError(f"{entry['url']}: replace text not found: {old!r}")
        text = text.replace(old, new)

    if "fill" in entry:
        text = fill(text, entry["fill"])
    if "viewBox" in entry:
        text = view_box(text, entry["viewBox"])

    return text.encode("utf-8")


def describe(entry):
    """The entry's edits in words, for the README."""
    edits = []
    if "fill" in entry:
        edits.append(f"filled {entry['fill']}")
    if "viewBox" in entry:
        edits.append("viewBox cropped")
    if entry.get("replace"):
        edits.append("text replaced")

    return ", ".join(edits)


def wrap_png(data):
    width, height = struct.unpack(">II", data[16:24])  # the IHDR chunk follows the magic
    encoded = base64.b64encode(data).decode("ascii")

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">'
        f'<image width="{width}" height="{height}" href="data:image/png;base64,{encoded}"/></svg>'
    )


def fill(text, color):
    """Paint a single-color icon: black and currentColor become `color`, and the root gets
    it as its color and (unless it sets one) default fill."""
    text = BLACK_RE.sub(rf'\1="{color}"', text)
    tag = SVG_TAG_RE.search(text).group()
    root = re.sub(r"\scolor=\"[^\"]*\"", "", tag)[:-1] + f' color="{color}"'
    if not re.search(r"\sfill=", tag):
        root += f' fill="{color}"'

    return text.replace(tag, root + ">", 1)


def view_box(text, box):
    """Crop to `box`; width and height go, so the build sizes the icon from the viewBox."""
    tag = SVG_TAG_RE.search(text).group()
    root = SIZE_ATTR_RE.sub("", tag)
    if re.search(r"\sviewBox=", root):
        root = re.sub(r'\sviewBox="[^"]*"', f' viewBox="{box}"', root)
    else:
        root = root[:-1] + f' viewBox="{box}">'

    return text.replace(tag, root, 1)
