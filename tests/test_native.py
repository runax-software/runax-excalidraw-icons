import json
from pathlib import PurePosixPath

from runax_icons.excalidraw import ElementFactory, NativeConverter
from runax_icons.excalidraw.elements import ICON_SIZE
from runax_icons.excalidraw.guidelines import Guidelines, LibraryFile
from runax_icons.excalidraw.native import Paint, _gradient_colors
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


def convert(svg: str, box: int = ICON_SIZE, anchor: bool = False) -> list[dict]:
    """The icon's elements: its shapes and caption, after its anchor when `anchor`."""
    converter = NativeConverter(ElementFactory(now=0))
    elements = [e.to_dict() for e in converter.icon(Icon(PurePosixPath("i.svg"), svg.encode()), "Icon", box=box)]
    return elements if anchor else elements[1:]


def test_an_invisible_rectangle_around_the_shapes_takes_arrows():
    # Excalidraw binds arrows to rectangles, not to lines; it's first so it paints under them.
    anchor, shape, caption = convert(svg('<rect x="0" y="2.5" width="10" height="5" fill="#000"/>'), anchor=True)
    assert anchor["type"] == "rectangle" and anchor["backgroundColor"] == anchor["strokeColor"] == "transparent"
    assert (anchor["x"], anchor["y"], anchor["width"], anchor["height"]) == (0, 16, 64, 32)
    assert anchor["groupIds"] == shape["groupIds"] == caption["groupIds"]


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


def svg(body: str, attrs: str = 'width="10" height="10" viewBox="0 0 10 10"') -> str:
    return f'<svg xmlns="http://www.w3.org/2000/svg" {attrs}>{body}</svg>'


def test_opacity_carries_over_and_invisible_shapes_go():
    # Grafana's signal icons: a faint background square under the symbol.
    faint, solid, _ = convert(svg(
        '<rect opacity="0.2" width="10" height="10" fill="#ff671d"/>'
        '<rect x="2" y="2" width="6" height="6" fill="#ff671d"/>'
        '<rect width="10" height="10" fill="#fff" fill-opacity="0"/>'
    ))
    assert (faint["opacity"], solid["opacity"]) == (20, 100)


def test_gradient_stop_opacity_makes_overlays_faint():
    # Dart's and Flutter's shading: a white or navy gradient fading to transparent.
    _, overlay, _ = convert(svg(
        '<defs><radialGradient id="g"><stop stop-color="#fff" stop-opacity="0.4"/>'
        '<stop stop-color="#fff" stop-opacity="0"/></radialGradient></defs>'
        '<rect width="10" height="10" fill="#0175c2"/><rect width="10" height="10" fill="url(#g)"/>'
    ))
    assert overlay["opacity"] == 20


def test_shapes_outside_the_viewbox_go_and_backgrounds_are_clipped():
    # A crop that drops a wordmark, an artboard leftover, and an oversized background.
    shapes = convert(svg(
        '<rect x="-20" y="-20" width="50" height="50" fill="#eee"/>'
        '<rect x="2" y="2" width="6" height="6" fill="#123456"/>'
        '<rect x="30" y="2" width="40" height="6" fill="#000"/>'
        '<rect x="-60" y="-60" width="5" height="5" fill="#000"/>'
    ))[:-1]
    assert [e["backgroundColor"] for e in shapes] == ["#eeeeee", "#123456"]
    background = shapes[0]
    assert (background["width"], background["height"]) == (ICON_SIZE, ICON_SIZE)


def test_stylesheet_rules_with_descendant_selectors_apply():
    # svglite's `.svglite rect { fill: none }`: without it, the frame rect paints black.
    shapes = convert(svg(
        "<style><![CDATA[ .svglite rect, .svglite polygon { fill: none; stroke: none; } ]]></style>"
        '<rect width="10" height="10"/><polygon points="2,2 8,5 2,8" style="fill: #000000;"/>',
        'class="svglite" width="10" height="10" viewBox="0 0 10 10"',
    ))[:-1]
    assert [e["backgroundColor"] for e in shapes] == ["#000000"]


def test_text_becomes_text_in_place():
    *_, text, caption = convert(svg(
        '<rect width="64" height="64" fill="#334155"/>'
        '<text x="32" y="40" text-anchor="middle" font-size="16" fill="#ffffff">REST</text>',
        'width="64" height="64" viewBox="0 0 64 64"',
    ))
    assert (text["text"], text["fontSize"], text["strokeColor"], text["textAlign"]) == ("REST", 16, "#ffffff", "center")
    assert abs(text["x"] + text["width"] / 2 - 32) < 0.01 and text["y"] < 40 < text["y"] + text["height"]
    assert caption["text"] == "Icon"


def test_gradients_average_their_stops_and_follow_references():
    colors = _gradient_colors(
        '<linearGradient id="stops"><stop stop-color="#000000"/><stop stop-color="#ffffff"/></linearGradient>'
        '<linearGradient id="placed" xlink:href="#stops" x1="0"/>'
    )
    assert colors == {"stops": Paint("#808080", 1.0), "placed": Paint("#808080", 1.0)}


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
