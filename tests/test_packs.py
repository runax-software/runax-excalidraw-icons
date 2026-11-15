import json

import pytest

from runax_icons.excalidraw import ElementFactory
from runax_icons.packs import PackBuilder, Validator
from runax_icons.workspace import AmbiguousIcon, IconNotFound, Workspace, WorkspaceError


def test_unknown_packs_are_an_error(workspace_root):
    with pytest.raises(WorkspaceError, match="unknown packs: nope"):
        Workspace(workspace_root).packs(["nope"])


def test_catalog_resolves_exact_labels_before_partial_ones(workspace_root):
    catalog = Workspace(workspace_root).catalog()
    assert catalog.resolve("queue").label == "Queue"  # exact, though "Queue Worker" also matches
    assert catalog.resolve("datab").label == "Database"
    with pytest.raises(AmbiguousIcon):
        catalog.resolve("ue")  # Queue and Queue Worker
    with pytest.raises(IconNotFound):
        catalog.resolve("kafka")


def test_validator_reports_unknown_samples(workspace_root):
    (pack,) = Workspace(workspace_root).packs()
    assert Validator(pack).problems() == []

    (workspace_root / "cloud" / "src" / "queue.svg").unlink()
    (problem,) = Validator(pack).problems()
    assert "README samples not found: Queue" in str(problem)


def test_builder_writes_library_scene_and_readme(workspace_root):
    (pack,) = Workspace(workspace_root).packs()
    result = PackBuilder(pack, ElementFactory(now=0)).build()

    assert result.icons == 3 and result.problems == []
    library = json.loads(pack.library_path.read_text())
    assert [item["name"] for item in library["libraryItems"]] == ["Database", "Queue", "Queue Worker"]
    assert pack.scene_path.exists()
    assert "drawn for the tests" in pack.readme_path.read_text()
