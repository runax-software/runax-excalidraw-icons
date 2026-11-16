import json
from pathlib import PurePosixPath

from runax_icons.excalidraw import ElementFactory, NativeConverter
from runax_icons.excalidraw.elements import ICON_SIZE
from runax_icons.excalidraw.guidelines import Guidelines, LibraryFile
from runax_icons.excalidraw.native import _gradient_colors
from runax_icons.icon import Icon
from runax_icons.packs import PackBuilder
from runax_icons.workspace import Workspace

from .conftest import SQUARE, write_pack

# A square ring (outer square with a square hole) over a solid blue square, like the
# kubernetes/community icons: the hole must show the blue, not cover it.
RING_OVER_BLUE = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 10 10">'
    '<rect width="10" height="10" fill="#326ce5"/>'
    '<path fill="#ffffff" fill-rule="evenodd" d="M0 0h10v10H0z M2 2v6h6V2z"/></svg>'
)


def convert(svg: str, box: int = ICON_SIZE) -> list[dict]:
    converter = NativeConverter(ElementFactory(now=0))
    return [e.to_dict() for e in converter.icon(Icon(PurePosixPath("i.svg"), svg.encode()), "Icon", box=box)]


def test_icon_becomes_grouped_lines_with_a_caption():
    *shapes, caption = convert(SQUARE)
    assert shapes and all(e["type"] == "line" and e["polygon"] for e in shapes)
    assert caption["type"] == "text" and caption["text"] == "Icon"
    assert len({tuple(e["groupIds"]) for e in [*shapes, caption]}) == 1


def test_shapes_fit_the_box():
    *shapes, _ = convert(SQUARE, box=48)
    xs = [e["x"] + x for e in shapes for x, _ in e["points"]]
    ys = [e["y"] + y for e in shapes for _, y in e["points"]]
    assert 0 <= min(xs) and max(xs) <= 48 and 0 <= min(ys) and max(ys) <= 48


def test_holes_are_joined_into_their_outline_not_painted_over():
    blue, ring, _ = convert(RING_OVER_BLUE)
    assert (blue["backgroundColor"], ring["backgroundColor"]) == ("#326ce5", "#ffffff")
    assert len(ring["points"]) > 5  # the outer square and the hole, as one outline
    # Document order is paint order: the blue square is drawn first, the ring's hole reveals it.
    assert [e["backgroundColor"] for e in (blue, ring)] == ["#326ce5", "#ffffff"]


def test_gradients_average_their_stops_and_follow_references():
    colors = _gradient_colors(
        '<linearGradient id="stops"><stop stop-color="#000000"/><stop stop-color="#ffffff"/></linearGradient>'
        '<linearGradient id="placed" xlink:href="#stops" x1="0"/>'
    )
    assert colors == {"stops": "#808080", "placed": "#808080"}


def test_publishable_packs_get_a_native_library_that_follows_the_guidelines(tmp_path):
    write_pack(tmp_path, "shapes", "title: S\nsource: s\npublish: true\nsources: [{files: '*.svg'}]\n",
               {"a.svg": SQUARE, "b.svg": RING_OVER_BLUE, "c.svg": SQUARE})
    (pack,) = Workspace(tmp_path).packs()
    PackBuilder(pack, ElementFactory(now=0)).build()

    library = json.loads(pack.native_library_path.read_text())
    assert not any(e["type"] == "image" for item in library["libraryItems"] for e in item["elements"])
    assert Guidelines().check(LibraryFile(pack.native_library_path)) == []


RASTER = (
    '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="10" height="10">'
    '<image width="10" height="10" xlink:href="data:image/png;base64,iVBORw0KGgo="/></svg>'
)


def test_every_pack_gets_a_native_library_without_its_raster_icons(tmp_path):
    write_pack(tmp_path, "shapes", "title: S\nsource: s\nsources: [{files: '*.svg'}]\n", {"a.svg": SQUARE, "photo.svg": RASTER})
    (pack,) = Workspace(tmp_path).packs()
    result = PackBuilder(pack, ElementFactory(now=0)).build()

    library = json.loads(pack.native_library_path.read_text())
    assert [item["name"] for item in library["libraryItems"]] == ["A"]
    assert result.not_native == ["Photo"]


def test_packs_that_forbid_native_get_no_native_library(tmp_path):
    write_pack(tmp_path, "logos", "title: L\nsource: s\nforbid: {native: terms}\nsources: [{files: '*.svg'}]\n", {"a.svg": SQUARE})
    (pack,) = Workspace(tmp_path).packs()
    PackBuilder(pack, ElementFactory(now=0)).build()
    assert not pack.native_library_path.exists()
