"""Package icon sets as Miro-style Excalidraw libraries.

Run with `uv run build.py` from the repo root (uv installs the locked dependencies):

  uv run build.py                    build every pack from its src/ (no network)
  uv run build.py k8s data           build only these packs
  uv run build.py --import           first refresh src/ from each pack's `import:` urls

Layout, one folder per pack (relative to this script):

  <pack>/pack.yml     title, import urls, sources, label overrides, README samples
  <pack>/src/         the SVGs the pack is built from (committed)
  <pack>/runax-<pack>.excalidrawlib and runax-<pack>.excalidraw
  <pack>/README.md    generated: source, icon count, a preview grid and the sources

Every folder with a pack.yml is a pack. An import downloads each url into a temporary
folder. An archive (zip or tar) replaces src/<into>/ with the largest size of each icon
(unlabeled variants preferred), skipping white-only icons (AWS `_Dark` variants, invisible
on a white canvas). A single SVG or PNG is written to src/<into> after the entry's edits
(fill, viewBox, replace; see builder/transform.py).

Each library item is a 64x64 image plus an editable label below it, grouped together.

Code lives in builder/: Pack (pack.py) drives each build, fetch (fetch.py) downloads,
transform (transform.py) edits imported files, IconSource (source.py) reads zips, tars and
folders, Icon (icon.py) derives size/label/fileId, ExcalidrawExporter (exporter.py) writes
the JSON, ReadmeRenderer (readme.py) writes the README.
"""

import argparse
import time
from pathlib import Path

from builder.pack import Pack

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("packs", nargs="*", help="packs to build (default: all)")
    parser.add_argument(
        "--import",
        dest="import_",
        action="store_true",
        help="refresh src/ from each pack's `import:` urls before building",
    )
    args = parser.parse_args()

    packs = Pack.discover(ROOT)
    unknown = set(args.packs) - {pack.name for pack in packs}
    if unknown:
        parser.error(f"unknown packs: {', '.join(sorted(unknown))}")

    now = int(time.time() * 1000)
    for pack in packs:
        if args.packs and pack.name not in args.packs:
            continue

        if args.import_:
            pack.import_icons()
        pack.build(now)


if __name__ == "__main__":
    main()
