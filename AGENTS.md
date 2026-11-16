# AGENTS.md

Guidance for AI coding agents working in this repository. Humans: see
[README.md](README.md) and [CONTRIBUTING.md](CONTRIBUTING.md).

## What this is

Miro-style Excalidraw icon libraries: each pack folder (`aws/`, `k8s/`, `data/`, ...) is built
from the SVGs in its `src/` into `runax-<pack>.excalidrawlib` (each item a 64px icon with an
editable label, grouped), `runax-<pack>.excalidraw` (a scene holding the images, which
Excalidraw needs because library files don't store them) and a generated `README.md`.

## Commands

```sh
uv run runax-icons build             # build every pack from src/ (no network)
uv run runax-icons build data k8s    # build some packs
uv run runax-icons import data       # re-download the pack's `import:` entries into src/, then build
uv run runax-icons check             # pack problems; must print "no problems"
uv run runax-icons search <text>     # find icons; `add` / `connect` edit .excalidraw diagrams
uv run runax-icons guidelines <pack> # libraries.excalidraw.com submission rules
uv run pytest                        # tests
uv run pyright                       # type checks
```

A change is done when `pytest`, `pyright` and `runax-icons check` pass, and any icon it touches
looks right rendered.

## Layout

The package `runax_icons/` is object-oriented, one responsibility per class:

- `cli.py`: Typer commands only (parse, call one object, print); domain errors become exit 1.
- `workspace.py`: `Workspace` (the packs under a root), and `Catalog`s that search and
  resolve pack icons (`IconCatalog`) or items of `.excalidrawlib` files (`LibraryCatalog`).
- `packs/`: `Pack` (a folder: config, paths, icons), `PackConfig` (pack.yml, validated),
  `imports.py` (`ArchiveImport`, `FileImport`, `NamesTemplate`: each knows what it covers and
  how to write itself), `Importer`, `Validator` (`Problem`s), `PackBuilder`,
  `ReadmeRenderer` (named so GitHub doesn't show it as a readme).
- `svg/`: `SvgDocument` (immutable; root tag, size, aspect, white-only, PNG wrapping) and the
  `Edit`s `Fill`, `ViewBox`, `Replace`.
- `excalidraw/`: typed elements built by `ElementFactory`, `Scene`, `Library` (writing) and
  `LibraryFile` (reading, images included), `Diagram` (add pack icons or library items, connect
  them), `Box` / `Point` geometry, `guidelines.py` (one `Rule` class per
  libraries.excalidraw.com guideline) and `NativeConverter` (SVG to native line elements, holes
  joined into their outline, for `publish: true` packs).
- `releases.py`: `Tag` (`<pack>/vX.Y.Z`), `Changelog` (release notes), `PackRelease` (a pack's
  assets and index entry) and `ReleaseIndex` (`index.json` and `llms.txt` of the `index`
  release), which let agents elsewhere use the icons with `gh` alone. Keep `llms.txt`'s
  instructions accurate: they
  are the whole interface for those agents.
- `icon.py` (`Icon`: naming from the path, fileId from the content), `sources.py` (folder,
  zip, tar readers), `download.py` (`Downloader`).
- `<pack>/pack.yml`: `title`, `source`, `license`, `native_size`, `publish`, `import:` (downloaded files and archives),
  `sources:` (hand-made files), `labels:` (file name → label), `samples:` (README preview).
- `<pack>/src/`: committed icons. `<pack>/CHANGELOG.md`: per-pack changes.

## Working on icons

Use the `icon-packs` skill (`.claude/skills/icon-packs/SKILL.md`, source in
`.apm/skills/icon-packs/`) for adding, fixing or removing icons and packs. In short: add an
`import:` entry, run `uv run runax-icons import <pack>`, look at the rendered icon, add a
`labels:` override if needed, and update the pack's `CHANGELOG.md`.

## Conventions

- Never edit generated files: pack `README.md`s and `runax-*` outputs come from `pack.yml`
  and `src/`. Commit `pack.yml`, `src/` and the regenerated `README.md` together; CI fails if a
  README is stale.
- Keep imported SVGs byte for byte as the build writes them. SVGs are exempt from line-ending
  normalization in `.gitattributes` and `.editorconfig` on purpose.
- Logos are trademarks: only crop or color them through declared edits, never redraw them, and
  never for vendors whose terms forbid it (Azure, AWS: no cropping, recoloring or reshaping).
  Record each pack's terms in `license:`, quoting the vendor where it publishes terms, and turn
  them into `forbid:` rules (`edit`, `native`, `publish`) on the pack or on single entries, with
  the reason. Never remove a `forbid:` rule to make a change pass.
- Python 3.11+: classes with one job each, type hints everywhere (`X | None`, never
  `Optional`), docstrings saying why, constants at module top. Dependencies: PyYAML, Typer,
  brotli, svgelements; keep it that way unless there's a strong reason.
- New behavior gets a test in `tests/`.
- Release notes go in the pack's `CHANGELOG.md` (icons) or the root `CHANGELOG.md` (build and
  repository), under `## [Unreleased]`, in Keep a Changelog format.

## Agent tooling

`apm install` (declared in `apm.yml`) sets up:

- the skills in `.claude/skills/`: `icon-packs` and `excalidraw-diagrams` (this repo's own,
  sources in `.apm/skills/`) and `github-actions-hardening` (for the CI workflow);
- the [Excalidraw MCP server](https://github.com/excalidraw/excalidraw-mcp) in `.mcp.json`, for
  freeform drawing;
- the Pyright language server in `.lsp.json` (needs `pyright-langserver` on the PATH:
  `uv tool install pyright`).
