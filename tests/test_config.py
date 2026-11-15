import pytest

from runax_icons.packs import ArchiveImport, ConfigError, FileImport, NamesTemplate, PackConfig
from runax_icons.svg import Fill, Replace, ViewBox


def parse(imports: list[dict]) -> PackConfig:
    return PackConfig.parse({"title": "T", "source": "s", "import": imports})


def test_entry_kind_follows_the_target():
    archive, single, template = parse(
        [
            {"url": "https://x/icons.zip", "into": "k8s", "path": "repo-*/icons"},
            {"url": "https://x/a.svg", "into": "a.svg"},
            {"url": "https://x/{src}.svg", "into": "{name}.svg", "names": {"A": "a-icon"}},
        ]
    ).imports
    assert isinstance(archive, ArchiveImport) and archive.path == "repo-*/icons"
    assert isinstance(single, FileImport)
    assert isinstance(template, NamesTemplate)


def test_names_expand_to_file_imports():
    (template,) = parse([{"url": "https://x/{src}.svg", "into": "p/{name}.svg", "names": {"Airbyte": "airbyte-icon"}}]).imports
    (target,) = template.targets()
    assert isinstance(target, FileImport)
    assert (target.url, target.into) == ("https://x/airbyte-icon.svg", "p/Airbyte.svg")
    assert template.files == "p/*.svg"


def test_edits_are_applied_replace_fill_viewbox():
    (entry,) = parse(
        [{"url": "u", "into": "a.svg", "viewBox": "0 0 1 1", "fill": "#000", "replace": [["a", "b"]]}]
    ).imports
    assert isinstance(entry, FileImport)
    assert [type(e) for e in entry.edits] == [Replace, Fill, ViewBox]


def test_archive_targets_cover_their_folder():
    archive = ArchiveImport(url="u", into="kubernetes")
    assert archive.covers("kubernetes/svg/pod.svg")
    assert not archive.covers("cncf/helm.svg")
    assert ArchiveImport(url="u").covers("anything.svg")


@pytest.mark.parametrize(
    "entry",
    [
        {"url": "u", "into": "a.svg", "viewbox": "0 0 1 1"},  # typo
        {"url": "u", "into": "folder", "fill": "#000"},  # edits on an archive
        {"url": "u", "into": "a.svg", "path": "x"},  # path on a file
        {"into": "a.svg"},  # no url
    ],
)
def test_invalid_entries_are_rejected(entry):
    with pytest.raises(ConfigError):
        parse([entry])


def test_unknown_top_level_keys_are_rejected():
    with pytest.raises(ConfigError, match="unknown keys"):
        PackConfig.parse({"title": "T", "source": "s", "lables": {}})
