import pytest

from runax_icons.excalidraw import ElementFactory
from runax_icons.packs import ConfigError, ForbiddenError, Operation, PackBuilder, PackConfig, Restrictions
from runax_icons.workspace import Workspace

from .conftest import SQUARE, write_pack


def parse(**extra) -> PackConfig:
    return PackConfig.parse({"title": "T", "source": "s", **extra})


def test_forbid_maps_known_operations_to_reasons():
    config = parse(forbid={"native": "the vendor's terms"})
    assert not config.forbid.allows(Operation.NATIVE)
    assert config.forbid.allows(Operation.EDIT)


def test_unknown_operations_are_an_error():
    with pytest.raises(ConfigError, match="unknown operations in forbid: nativ"):
        parse(forbid={"nativ": "typo"})


def test_publishing_needs_native_shapes_allowed():
    with pytest.raises(ForbiddenError, match="`native` is forbidden here: terms"):
        parse(publish=True, forbid={"native": "terms"})


def test_edits_are_refused_by_the_pack_or_their_entry():
    entry = {"url": "https://x/logo.svg", "into": "logo.svg", "fill": "#000"}
    with pytest.raises(ForbiddenError, match="`edit`"):
        parse(forbid={"edit": "terms"}, **{"import": [entry]})
    with pytest.raises(ForbiddenError, match="trademark policy"):
        parse(**{"import": [{**entry, "forbid": {"edit": "trademark policy"}}]})


def test_restrictions_combine():
    combined = Restrictions({Operation.EDIT: "pack"}) | Restrictions({Operation.NATIVE: "entry"})
    assert not combined.allows(Operation.EDIT) and not combined.allows(Operation.NATIVE)


def test_native_library_leaves_out_icons_whose_entry_forbids_it(tmp_path):
    write_pack(
        tmp_path,
        "mixed",
        """title: M
source: s
publish: true
sources:
  - files: "logo.svg"
    forbid: {native: a trademark}
  - files: "*.svg"
""",
        {"logo.svg": SQUARE, "a.svg": SQUARE, "b.svg": SQUARE},
    )
    (pack,) = Workspace(tmp_path).packs()
    result = PackBuilder(pack, ElementFactory(now=0)).build()
    assert result.not_native == ["Logo"]
