import json
from pathlib import Path, PurePosixPath

from runax_icons.excalidraw import Diagram, ElementFactory, Library, NativeConverter, Point
from runax_icons.excalidraw.library_file import LibraryFile
from runax_icons.icon import Icon
from runax_icons.workspace import LibraryCatalog

from .conftest import SQUARE


def image_library(tmp_path: Path, names: list[str]) -> Path:
    """One of our libraries: image items, their SVGs in the top-level `files` map."""
    factory, library = ElementFactory(now=0), None
    library = Library(factory)
    for name in names:
        library.add_icon(Icon(PurePosixPath(f"{name}.svg"), SQUARE.encode()), name)
    path = tmp_path / "icons.excalidrawlib"
    library.save(path)
    return path


def native_library(tmp_path: Path) -> Path:
    factory = ElementFactory(now=0)
    library = Library(factory)
    library.add_item("Queue", NativeConverter(factory).icon(Icon(PurePosixPath("q.svg"), SQUARE.encode()), "Queue"))
    path = tmp_path / "native.excalidrawlib"
    library.save(path)
    return path


def test_items_get_the_files_their_images_use(tmp_path):
    (database,) = LibraryFile(image_library(tmp_path, ["Database"])).items
    (image,) = [e for e in database.elements if e["type"] == "image"]
    assert database.name == "Database" and set(database.files) == {image["fileId"]}


def test_per_item_files_are_read_too(tmp_path):
    path = image_library(tmp_path, ["Database"])
    data = json.loads(path.read_text())
    data["libraryItems"][0]["files"], data["files"] = data.pop("files"), {}
    path.write_text(json.dumps(data))
    (item,) = LibraryFile(path).items
    assert item.files


def test_catalog_searches_across_libraries(tmp_path):
    catalog = LibraryCatalog([image_library(tmp_path, ["Database", "Cache"]), native_library(tmp_path)])
    assert [m.label for m in catalog.search("")] == ["Database", "Cache", "Queue"]
    assert catalog.resolve("queue").source == "native.excalidrawlib"


def test_added_items_get_fresh_ids_their_files_and_a_new_caption(tmp_path):
    (item,) = LibraryFile(image_library(tmp_path, ["Database"])).items
    diagram = Diagram(tmp_path / "d.excalidraw", ElementFactory(now=1))
    diagram.add_library_item(item, Point(0, 0))
    diagram.add_library_item(item, Point(300, 0), label="Orders DB")

    ids = [e["id"] for e in diagram.scene.elements]
    assert len(ids) == len(set(ids)) == 4  # the same item twice, no clashing ids
    assert set(diagram.icons()) == {"database", "orders db"}
    assert set(diagram.scene.files) == set(item.files)


def test_arrows_bind_to_native_icons_through_their_anchor(tmp_path):
    diagram = Diagram(tmp_path / "d.excalidraw", ElementFactory(now=1))
    (queue,) = LibraryFile(native_library(tmp_path)).items
    diagram.add_library_item(queue, Point(0, 0))
    diagram.add_library_item(queue, Point(300, 0), label="Retries")
    diagram.connect("Queue", "Retries")

    arrow = next(e for e in diagram.scene.elements if e["type"] == "arrow")
    ends = [e for e in diagram.scene.elements if e["id"] in (arrow["startBinding"]["elementId"], arrow["endBinding"]["elementId"])]
    assert len(ends) == 2
    assert all(e["type"] == "rectangle" and e["strokeColor"] == e["backgroundColor"] == "transparent" for e in ends)
    assert all(e["boundElements"] == [{"id": arrow["id"], "type": "arrow"}] for e in ends)


def test_arrows_to_line_only_icons_stay_unbound(tmp_path):
    # Other libraries' line-drawn items have nothing Excalidraw binds arrows to.
    path = native_library(tmp_path)
    data = json.loads(path.read_text())
    for item in data["libraryItems"]:
        item["elements"] = [e for e in item["elements"] if e["type"] != "rectangle"]
    path.write_text(json.dumps(data))

    diagram = Diagram(tmp_path / "d.excalidraw", ElementFactory(now=1))
    (queue,) = LibraryFile(path).items
    (database,) = LibraryFile(image_library(tmp_path, ["Database"])).items
    diagram.add_library_item(queue, Point(0, 0))
    diagram.add_library_item(database, Point(300, 0))
    diagram.connect("Queue", "Database")

    arrow = next(e for e in diagram.scene.elements if e["type"] == "arrow")
    assert arrow["startBinding"] is None and arrow["endBinding"]["elementId"] == diagram.find_icon("Database")["id"]
