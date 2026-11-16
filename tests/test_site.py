import json

from runax_icons.excalidraw import ElementFactory
from runax_icons.packs import PackBuilder
from runax_icons.site import SiteExporter
from runax_icons.workspace import Workspace

from .conftest import SQUARE, write_pack


def test_site_has_libraries_index_and_llms_txt(tmp_path):
    write_pack(
        tmp_path / "packs",
        "cloud",
        "title: Cloud\nsource: s\nlicense: diagrams only\nsources: [{files: '**'}]\n",
        {"a.svg": SQUARE, "b.svg": SQUARE},
    )
    (pack,) = Workspace(tmp_path / "packs").packs()
    PackBuilder(pack, ElementFactory(now=0)).build()
    SiteExporter([pack], tmp_path / "site", "https://icons.example").export()

    index = json.loads((tmp_path / "site" / "index.json").read_text())
    (entry,) = index["packs"]
    assert entry["library"] == "https://icons.example/cloud/runax-cloud.excalidrawlib"
    assert entry["labels"] == ["A", "B"] and entry["icons"] == 2 and entry["license"] == "diagrams only"
    assert "groups" not in entry
    assert (tmp_path / "site" / "cloud" / "runax-cloud.excalidrawlib").exists()

    llms = (tmp_path / "site" / "llms.txt").read_text()
    assert "https://icons.example/index.json" in llms
    assert "[Cloud](https://icons.example/cloud/runax-cloud.excalidrawlib): 2 icons" in llms
