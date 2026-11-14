"""Package icon sets as Miro-style Excalidraw libraries.

Run with `uv run build.py` from the repo root (uv installs the locked dependencies).

Layout, one folder per pack (relative to this script):

  <pack>/pack.yml     title, source, download glob, label overrides, README samples
  <pack>/downloads/   raw packages, as downloaded (zip files or folders)
  <pack>/icons/       exactly the SVGs that went into the library
  <pack>/<pack>.excalidrawlib and <pack>.excalidraw
  <pack>/README.md    generated: source, icon count and a preview grid of sample icons

Every folder with a pack.yml is a pack. The newest download matching its `download` glob
wins; without one, the pack is rebuilt from <pack>/icons/.

Each library item is a 64x64 image plus an editable label below it, grouped together.
Only the largest size of each icon is kept (unlabeled variants preferred), and white-only
icons (AWS `_Dark` variants, meant for dark backgrounds) are skipped because they are
invisible on a white canvas.

Code lives in builder/: Pack (pack.py) drives each build, IconSource (source.py) reads
zips and folders, Icon (icon.py) derives size/label/fileId, ExcalidrawExporter
(exporter.py) writes the JSON, ReadmeRenderer (readme.py) writes the README.
"""

import time
from pathlib import Path

from builder.pack import Pack

ROOT = Path(__file__).resolve().parent


def main():
    now = int(time.time() * 1000)
    for pack in Pack.discover(ROOT):
        pack.build(now)


if __name__ == "__main__":
    main()
