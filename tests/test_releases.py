import json

import pytest

from runax_icons.excalidraw import ElementFactory
from runax_icons.packs import PackBuilder
from runax_icons.releases import Changelog, PackRelease, ReleaseError, ReleaseIndex, Tag
from runax_icons.workspace import Workspace

from .conftest import SQUARE, write_pack

CHANGELOG = """# Changelog

## [Unreleased]

## [1.1.0] - 2026-11-16

### Added

- B.

## [1.0.0] - 2026-11-01

- A.
"""


def cloud_pack(root):
    folder = write_pack(
        root, "cloud", "title: Cloud\nsource: s\nlicense: diagrams only\nsources: [{files: '**'}]\n", {"a.svg": SQUARE, "b.svg": SQUARE}
    )
    (folder / "CHANGELOG.md").write_text(CHANGELOG)
    (pack,) = Workspace(root).packs()
    PackBuilder(pack, ElementFactory(now=0)).build()
    return pack


@pytest.mark.parametrize("tag", ["v1.0.0", "aws/1.0.0", "aws/v1.0", "AWS/v1.0.0", "a/b/v1.0.0"])
def test_tags_name_a_pack_and_a_version(tag):
    with pytest.raises(ReleaseError):
        Tag.parse(tag)


def test_tag_round_trips():
    assert Tag.parse("k8s/v1.2.3-rc.1") == Tag("k8s", "1.2.3-rc.1")
    assert str(Tag("k8s", "1.2.3")) == "k8s/v1.2.3"


def test_notes_are_the_versions_changelog_section(tmp_path):
    path = tmp_path / "CHANGELOG.md"
    path.write_text(CHANGELOG)
    assert Changelog(path).notes("1.1.0") == "### Added\n\n- B.\n"
    assert Changelog(path).notes("1.0.0") == "- A.\n"
    with pytest.raises(ReleaseError, match="no `## \\[2.0.0\\]`"):
        Changelog(path).notes("2.0.0")


def test_release_writes_libraries_scene_and_entry(tmp_path):
    pack = cloud_pack(tmp_path / "packs")
    assets = PackRelease(pack, Tag("cloud", "1.1.0")).write(tmp_path / "dist")

    assert [a.name for a in assets] == ["runax-cloud.excalidrawlib", "runax-cloud.excalidraw", "runax-cloud-native.excalidrawlib", "runax-cloud.json"]
    entry = json.loads(assets[-1].read_text())
    assert entry["release"] == "cloud/v1.1.0" and entry["library"] == "runax-cloud.excalidrawlib"
    assert entry["labels"] == ["A", "B"] and entry["license"] == "diagrams only"


def test_tag_must_match_the_pack(tmp_path):
    pack = cloud_pack(tmp_path / "packs")
    with pytest.raises(ReleaseError, match="not 'cloud'"):
        PackRelease(pack, Tag("aws", "1.0.0"))


def test_index_merges_entries_and_explains_gh_downloads(tmp_path):
    pack = cloud_pack(tmp_path / "packs")
    PackRelease(pack, Tag("cloud", "1.1.0")).write(tmp_path / "entries")
    ReleaseIndex.load(tmp_path / "entries", "owner/icons").write(tmp_path / "index")

    index = json.loads((tmp_path / "index" / "index.json").read_text())
    assert index["repository"] == "owner/icons"
    assert [p["release"] for p in index["packs"]] == ["cloud/v1.1.0"]

    llms = (tmp_path / "index" / "llms.txt").read_text()
    assert "gh release download index -R owner/icons -p index.json" in llms
    assert "- Cloud (`cloud`), release `cloud/v1.1.0`: `runax-cloud.excalidrawlib`, native shapes `runax-cloud-native.excalidrawlib`, 2 icons" in llms
