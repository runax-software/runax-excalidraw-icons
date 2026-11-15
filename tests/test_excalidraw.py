from pathlib import Path, PurePosixPath

import pytest

from runax_icons.excalidraw import Box, Diagram, DiagramError, ElementFactory, Point
from runax_icons.icon import Icon

from .conftest import SQUARE


def test_edge_toward_leaves_the_box_on_the_facing_side():
    box = Box(0, 0, 100, 50)
    assert box.edge_toward(Point(300, 25)) == Point(100, 25)
    assert box.edge_toward(Point(50, 200), gap=8) == Point(50, 58)


def new_diagram(tmp_path: Path) -> Diagram:
    diagram = Diagram(tmp_path / "d.excalidraw", ElementFactory(now=0))
    icon = Icon(PurePosixPath("db.svg"), SQUARE.encode())
    diagram.add_icon(icon, "Database", Point(0, 0))
    diagram.add_icon(icon, "Cache")
    return diagram


def test_add_icon_groups_image_and_caption_and_embeds_the_file(tmp_path):
    diagram = new_diagram(tmp_path)
    image, caption = diagram.scene.elements[:2]
    assert image["groupIds"] == caption["groupIds"]
    assert image["fileId"] in diagram.scene.files
    assert len(diagram.scene.files) == 1  # same content, one file


def test_icons_without_a_position_go_right_of_the_drawing(tmp_path):
    diagram = new_diagram(tmp_path)
    cache = diagram.find_icon("cache")
    assert cache["x"] > diagram.find_icon("Database")["x"] + 64


def test_connect_binds_the_arrow_to_both_icons(tmp_path):
    diagram = new_diagram(tmp_path)
    diagram.connect("Database", "cache", label="reads")
    arrow, text = diagram.scene.elements[-2:]

    assert arrow["type"] == "arrow" and text["containerId"] == arrow["id"]
    assert arrow["startBinding"]["elementId"] == diagram.find_icon("Database")["id"]
    assert {"id": arrow["id"], "type": "arrow"} in diagram.find_icon("Cache")["boundElements"]


def test_save_and_reload_keeps_the_icons(tmp_path):
    diagram = new_diagram(tmp_path)
    diagram.save()
    reloaded = Diagram(diagram.path, ElementFactory(now=1))
    assert set(reloaded.icons()) == {"database", "cache"}


def test_connect_reports_unknown_and_self_connections(tmp_path):
    diagram = new_diagram(tmp_path)
    with pytest.raises(DiagramError, match="no icon labeled"):
        diagram.connect("Database", "Queue")
    with pytest.raises(DiagramError, match="itself"):
        diagram.connect("Database", "database")
