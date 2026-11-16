import base64
import struct
import zlib

import pytest

from runax_icons.svg import EditError, Fill, Replace, SvgDocument, SvgError, ViewBox

from .conftest import SQUARE, WIDE_VIEWBOX_ONLY


def png(width: int, height: int) -> bytes:
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    chunk = lambda kind, data: struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IEND", b"")


def test_aspect_comes_from_the_viewbox_first():
    assert SvgDocument.from_text(WIDE_VIEWBOX_ONLY).aspect == 2


def test_rendered_gives_viewbox_only_svgs_an_absolute_size():
    rendered = SvgDocument.from_text(WIDE_VIEWBOX_ONLY).rendered()
    assert 'width="256" height="128.0"' in rendered.root_tag  # format feeds the fileId: keep it


def test_rendered_keeps_sized_svgs_byte_for_byte():
    document = SvgDocument.from_text(SQUARE)
    assert document.rendered().data == document.data


def test_png_is_wrapped_at_its_own_size():
    data = png(30, 20)
    document = SvgDocument.from_download(data)
    assert 'viewBox="0 0 30 20"' in document.root_tag
    assert base64.b64encode(data).decode() in document.text


def test_white_only_needs_every_painted_shape_white():
    white = '<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0" fill="#fff"/></svg>'
    unfilled = '<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0" fill="#fff"/><path d="M1 1"/></svg>'
    assert SvgDocument.from_text(white).is_white_only
    assert not SvgDocument.from_text(unfilled).is_white_only  # the unfilled path renders black


def test_root_tag_is_required():
    with pytest.raises(SvgError):
        SvgDocument.from_text("<html>not found</html>").root_tag


def test_fill_paints_black_and_the_root():
    icon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M0 0" fill="currentColor"/></svg>'
    filled = Fill("#F38020").apply(SvgDocument.from_text(icon))
    assert 'fill="#F38020"' in filled.text and 'color="#F38020"' in filled.root_tag
    assert "currentColor" not in filled.text


def test_viewbox_crops_and_drops_the_size():
    cropped = ViewBox("0 0 12 12").apply(SvgDocument.from_text(SQUARE))
    assert 'viewBox="0 0 12 12"' in cropped.root_tag
    assert "width=" not in cropped.root_tag


SINGLE_QUOTED = "<svg xmlns='http://www.w3.org/2000/svg' width='200pt' height='100pt' viewBox='0 0 200 100'><path d='M0 0' fill='black'/></svg>"


def test_single_quoted_attributes_are_read_and_edited():
    document = SvgDocument.from_text(SINGLE_QUOTED)
    assert document.aspect == 2 and document.has_absolute_size

    cropped = ViewBox("0 0 50 50").apply(document)
    assert 'viewBox="0 0 50 50"' in cropped.root_tag and "0 0 200 100" not in cropped.root_tag
    assert "width=" not in cropped.root_tag
    assert cropped.rendered().root_tag.count("width=") == 1  # one width, or parsers reject it

    filled = Fill("#F38020").apply(document)
    assert 'fill="#F38020"' in filled.text and "'black'" not in filled.text


def test_replace_fails_when_upstream_changed():
    with pytest.raises(EditError):
        Replace("opacity=0.2", "opacity=0.15").apply(SvgDocument.from_text(SQUARE))


def test_edits_describe_themselves():
    assert [e.describe() for e in (Fill("#000"), ViewBox("0 0 1 1"), Replace("a", "b"))] == [
        "filled #000",
        "viewBox cropped",
        "text replaced",
    ]


def lossless_webp(width: int, height: int) -> bytes:
    bits = (width - 1) | ((height - 1) << 14)
    chunk = b"VP8L" + (5).to_bytes(4, "little") + b"\x2f" + bits.to_bytes(4, "little")
    return b"RIFF" + (4 + len(chunk)).to_bytes(4, "little") + b"WEBP" + chunk


def test_webp_is_recognized_by_content_and_wrapped_at_its_size():
    document = SvgDocument.from_download(lossless_webp(328, 200))
    assert 'viewBox="0 0 328 200"' in document.root_tag
    assert "data:image/webp;base64," in document.text


def test_downloads_that_arent_svg_are_rejected():
    with pytest.raises(SvgError):
        SvgDocument.from_download(b"<html><body>404 Not Found</body></html>")
