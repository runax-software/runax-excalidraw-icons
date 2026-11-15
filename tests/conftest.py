from pathlib import Path

import pytest

SQUARE = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path d="M0 0h24v24H0z" fill="#f00"/></svg>'
WIDE_VIEWBOX_ONLY = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 100"><rect width="200" height="100" fill="#0a0"/></svg>'


def write_pack(root: Path, name: str, pack_yml: str, files: dict[str, str]) -> Path:
    """A pack folder with a pack.yml and the given files (path -> SVG text) in src/."""
    pack = root / name
    (pack / "src").mkdir(parents=True)
    (pack / "pack.yml").write_text(pack_yml)
    for path, svg in files.items():
        target = pack / "src" / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(svg)
    return pack


@pytest.fixture
def workspace_root(tmp_path: Path) -> Path:
    write_pack(
        tmp_path,
        "cloud",
        """title: Cloud
source: test icons
labels:
  db: Database
sources:
  - files: "*.svg"
    note: drawn for the tests
samples: [Database, Queue]
""",
        {"db.svg": SQUARE, "queue.svg": SQUARE, "queue-worker.svg": WIDE_VIEWBOX_ONLY},
    )
    return tmp_path
