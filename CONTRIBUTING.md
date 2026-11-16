# Contributing

Thanks for helping! Icons and packs are plain files plus a `pack.yml`, so most changes need no
code.

## Setup

Install [uv](https://docs.astral.sh/uv/), then from the repo root:

```sh
uv run runax-icons build             # build every pack from its src/ (no network)
uv run runax-icons build k8s data    # build only these packs
uv run runax-icons import data       # refresh src/ from the pack's `import:` urls, then build
uv run runax-icons check             # report pack problems; exit 1 if there are any
uv run runax-icons guidelines k8s    # check a library against the libraries.excalidraw.com rules
uv run runax-icons release aws/v1.0.0  # a pack's release assets, into dist/
uv run pytest && uv run pyright      # tests and type checks
```

uv installs the package and its locked dependencies into `.venv/` on first run. Every folder
with a `pack.yml` is a pack, built from every SVG in its `src/` into `runax-<pack>.excalidrawlib`,
`runax-<pack>.excalidraw` (both git-ignored) and its `README.md` (generated, committed).

## Layout

```
runax_icons/                    the `runax-icons` package and command line
  cli.py                        commands (Typer)
  workspace.py                  Workspace (the packs in a folder), catalogs of pack icons and
                                library items (search, resolve)
  packs/                        Pack, PackConfig (pack.yml), import entries, Importer,
                                Validator, PackBuilder, ReadmeRenderer
  svg/                          SvgDocument, edits (Fill, ViewBox, Replace)
  excalidraw/                   typed elements, Scene, Library, LibraryFile (reading libraries),
                                Diagram, geometry, guidelines, NativeConverter (icons as native shapes)
  releases.py                   pack releases (tags, notes, assets) and the index release
  icon.py, sources.py           Icon (naming, fileId); folder, zip and tar readers
  download.py                   Downloader (temporary folder, parallel)
tests/                          pytest suite
<pack>/
  pack.yml                      title, license, forbid, imports, hand-made sources, labels,
                                README samples, native_size, publish
  src/                          the SVGs the pack is built from (committed)
  CHANGELOG.md                  the pack's changes
  README.md                     generated preview, license and sources of the pack
```

## Code changes

The `runax_icons` package is laid out [above](#layout) and described class by
class in [AGENTS.md](AGENTS.md#layout). Before opening a pull request:

```sh
uv run pytest       # add a test for new behavior
uv run pyright      # type hints everywhere, `X | None` rather than Optional
```

## AI agents

The repo ships agent tooling through [APM](https://github.com/microsoft/apm): run `apm install`
to deploy the skills in `.claude/skills/` (`icon-packs` covers the steps below,
`excalidraw-diagrams` drawing with the packs), the Excalidraw MCP server in `.mcp.json` and the
Pyright language server in `.lsp.json`. [AGENTS.md](AGENTS.md) is the guide for agents.

## Adding an icon

1. Prefer an official source: the project's own repository or website, or an open collection
   ([gilbarbara/logos](https://github.com/gilbarbara/logos),
   [simple-icons](https://github.com/simple-icons/simple-icons),
   [lobe-icons](https://github.com/lobehub/lobe-icons), [cncf/artwork](https://github.com/cncf/artwork)).
   Use the icon (mark) rather than the full wordmark, in color where one exists.
2. Add an `import:` entry to the pack's `pack.yml` with its url and the target file in `src/`,
   plus any edits it needs (`viewBox` to crop off a wordmark, `fill` to color a single-color icon,
   `replace` for small text fixes). See [pack.yml](#packyml) for the format.
3. Run `uv run runax-icons import <pack>`, which downloads it into `src/` and builds the pack.
4. If the file name doesn't make a good label, add it under `labels:`. Add it to `samples:` if it
   belongs in the README preview.
5. Check the icon in the pack's generated README or in Excalidraw, run `uv run runax-icons check`,
   and commit `pack.yml`, `src/` and `README.md`.

Files that can't be imported (drawn by hand, cut out of a raster image, no stable url) go in
`src/` directly, with an entry under `sources:` saying where they came from. The build warns
about files in `src/` that no `import:` or `sources:` entry covers.

## pack.yml

Files in `src/` are either imported or hand-made. `runax-icons import` downloads the `import:`
entries into a temporary folder and writes the results to `src/`, so nothing is cached in the
repo:

```yaml
import:
  # An archive (zip or tar) replaces the folder src/<into>/ (default: all of src/) with the
  # largest size of each icon, skipping white-only ones (AWS `_Dark` variants).
  - url: https://github.com/kubernetes/community/archive/<commit>.zip
    path: "community-*/icons"          # optional: folder inside the archive
    into: kubernetes
  # A single SVG (or PNG/WebP, wrapped in an SVG) is written to src/<into> after optional edits.
  - url: https://caddyserver.com/resources/images/logo-light.svg
    into: other/caddy.svg
    viewBox: "-2 -2 152 151"           # crop, e.g. to drop a wordmark
  # `names` expands one entry per name, filling {name} (and {src}, for a map) in url and into.
  - url: https://raw.githubusercontent.com/cloudflare/cloudflare-docs/production/src/icons/{name}.svg
    into: "products/{name}.svg"
    fill: "#F38020"                    # paint black / currentColor in this color
    names: [workers, r2, d1]
```

Other edits: `replace: [[old, new], ...]` for text. To move to a new upstream release, change
the url and run `uv run runax-icons import <pack>`. Hand-made files (drawn, cropped from a PNG,
or with no known url) are listed under `sources:` instead, so every file in `src/` has a
recorded origin.

What a pack's icons may be put through follows from their terms:

```yaml
forbid:                     # on the pack, or on a single import/sources entry
  edit: Microsoft's terms forbid cropping, recoloring or reshaping the icons
  native: redrawing the icons as native shapes changes their shape
  publish: Microsoft permits the icons only in diagrams, training materials or documentation
```

`edit` covers `fill`, `viewBox` and `replace` on imports, `native` the native-shape library, and
`publish` `publish: true` (for libraries.excalidraw.com). Every pack also gets
`runax-<pack>-native.excalidrawlib`, unless it forbids `native`; icons with no paths to trace
(raster images) are left out of it. The build refuses a forbidden edit or `publish: true` with the
reason, and leaves icons whose entry forbids `native` out of the native library.
`native_size: true` keeps the vendor's icon sizes (AWS: 64px services, 48px resources, 32px
groups) instead of making every icon 64px.

`build` and `check` report files in `src/` that no entry covers, `sources:` entries that match
nothing, imported files missing from `src/` and README samples that aren't labels. Unknown keys
are errors.

## Adding a pack

Create `<pack>/pack.yml` with a `title`, `source`, `license` and its `import:` / `sources:`
entries, then run `uv run runax-icons import <pack>`. Every folder with a `pack.yml` is a pack.

## CI and releases

`.github/workflows/ci.yml` runs only what a pull request affects: tests and type checks when
Python code changes, and a build, `check` and guidelines check for each changed pack. The single
`ci` check is green when everything that ran passed.

`release.yml` publishes a pack's release for each `<pack>/vX.Y.Z` tag, then refreshes the
`index` release that agents read: see [RELEASING.md](RELEASING.md).

## Licensing

Only add icons whose license or terms allow redistribution for diagrams, and record that in
the pack's `license`. Product logos are trademarks of their owners: use them unmodified apart
from cropping and coloring, and don't add icons that suggest an endorsement.
