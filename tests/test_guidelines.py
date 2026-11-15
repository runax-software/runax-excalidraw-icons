import json
from pathlib import Path

from runax_icons.excalidraw.guidelines import (
    EnglishOnly,
    EnoughItems,
    Grouped,
    Guidelines,
    LibraryFile,
    NoImages,
    NotTrivial,
    StandsAlone,
)


def element(kind: str, groups: list[str] | None = None, **fields) -> dict:
    return {"type": kind, "groupIds": groups or [], **fields}


def library(tmp_path: Path, items: list[dict]) -> LibraryFile:
    path = tmp_path / "lib.excalidrawlib"
    path.write_text(json.dumps({"type": "excalidrawlib", "version": 2, "libraryItems": items}))
    return LibraryFile(path)


def item(name: str, *elements: dict) -> dict:
    return {"name": name, "elements": list(elements)}


def icon_item(name: str) -> dict:
    """A drawn icon: shapes and a caption, grouped."""
    return item(
        name,
        element("rectangle", ["g"]),
        element("ellipse", ["g"]),
        element("line", ["g"]),
        element("text", ["g"], originalText=name),
    )


def test_a_good_library_follows_every_rule(tmp_path):
    good = library(tmp_path, [icon_item("Queue"), icon_item("Database"), icon_item("Cache")])
    assert Guidelines().check(good) == []


def test_a_lone_basic_shape_is_trivial(tmp_path):
    lib = library(tmp_path, [item("Box", element("rectangle"))])
    assert NotTrivial().check(lib) == ["Box: only a basic shape"]


def test_non_latin_text_is_flagged_but_accents_are_fine(tmp_path):
    lib = library(tmp_path, [icon_item("Café"), icon_item("データベース")])
    messages = EnglishOnly().check(lib)
    assert messages and all("データベース" in m for m in messages)  # its name and caption


def test_items_need_elements_and_names(tmp_path):
    lib = library(tmp_path, [item("Empty"), {"elements": [element("rectangle")]}])
    assert StandsAlone().check(lib) == ["Empty: empty", "an item has no name"]


def test_a_library_needs_three_items(tmp_path):
    assert EnoughItems().check(library(tmp_path, [icon_item("A"), icon_item("B")])) == ["2 items"]


def test_multi_element_items_must_share_a_group(tmp_path):
    lib = library(tmp_path, [item("Loose", element("rectangle", ["a"]), element("text", ["b"]))])
    assert Grouped().check(lib) == ["Loose: elements not grouped"]


def test_image_items_cant_be_published(tmp_path):
    lib = library(tmp_path, [item("Logo", element("image", ["g"]), element("text", ["g"]))])
    (message,) = NoImages().check(lib)
    assert message.startswith("1 of 1 items are images")
