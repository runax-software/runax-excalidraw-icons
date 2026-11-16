# Changelog

All notable changes to the `runax-icons` package and command line, and to the repository, are documented in
this file. Each pack has its own `CHANGELOG.md` for its icons.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
The command line isn't released (it's for working on this repository); each pack is, tagged
`<pack>/vX.Y.Z`.

## [Unreleased]

## [0.1.0] - 2026-11-16

### Added

- `runax-icons`, a command line (Typer) for the packs and for diagrams:
  - `build` writes each pack's `runax-<pack>.excalidrawlib`, a `runax-<pack>.excalidraw`
    scene holding the images, and a README with a preview grid, the icons' license and their
    sources.
  - `import` refreshes `src/` from the `import:` list in each `pack.yml`: archives (keeping the
    largest size of each icon and skipping white-only ones) and single SVG or PNG files with
    declared edits (`fill`, `viewBox`, `replace`, `names` templates).
  - `check` reports pack problems (uncovered files, unused sources, missing imports, unknown
    README samples) and exits 1 if there are any.
  - `search` finds icons across packs; `add` puts one into an `.excalidraw` diagram with its
    image embedded; `connect` draws an arrow between two icons by caption, bound to both.
  - `guidelines` checks built libraries against the libraries.excalidraw.com submission
    guidelines (trivial items, English only, items that stand alone, at least three items,
    grouping, and images, which that site can't store); CI enforces it for `publish: true` packs.
- Every pack also builds `runax-<pack>-native.excalidrawlib`: icons converted into native
  Excalidraw shapes (holes joined into their outlines, gradients as their average color and
  opacity, text as text, shapes clipped to the viewBox, and an invisible rectangle around each
  icon that arrows bind to), which work in Excalidraw's library panel on their own, as
  Excalidraw drops a library's images on import; raster icons are left out. `guidelines` checks it for `publish: true` packs.
- `forbid:` in `pack.yml`, on a pack or a single entry, rules out operations its icons' terms
  don't allow (`edit`, `native`, `publish`), with the reason; the build refuses them, and every
  pack declares its rules.
- `search` and `add` work from `.excalidrawlib` files too (`--library`, or `RUNAX_ICONS_LIBRARY`):
  items are placed with fresh ids and their images, from ours or any other library, so diagrams
  can be built from libraries that aren't published anywhere, by people or agents.
- Each pack is released on its own with a `<pack>/vX.Y.Z` tag: `release` builds its libraries,
  scene and a `runax-<pack>.json` entry, with notes from the pack's changelog. The `index`
  release then holds `index.json` (every pack's latest release, icon names and terms) and
  `llms.txt`, which explains to agents how to download them with `gh` and put icons into an
  `.excalidraw` file
  with no tooling.
- `pack.yml` is validated on load: unknown keys and misplaced options are errors.
- `native_size: true` draws a pack's icons at their designed size (AWS: 64px services, 48px
  resources, 32px groups), as AWS's guidelines ask.
- Captions follow vendor naming rules: at most two lines, never "AWS" or "Amazon" alone on a
  line, and small words ("and", "for") lowercase.
- Pack README previews keep each icon's proportions.
- `NOTICE.md` and `LICENSES/`: copyright notices, license texts and our changes for every openly
  licensed icon set, shipped with each release.
- Imports recognize WebP as well as PNG, by content rather than file name, and reject downloads
  that aren't images (an error page no longer lands in `src/`).
- Non-square icons keep their aspect ratio, and SVGs without a size render at their real shape.
- CI runs only what a change affects: a paths-filter job finds changed Python code and changed
  packs, then tests and type-checks the package and builds, checks and guideline-checks each
  changed pack in parallel (every pack when the build code changed); one `ci` job sums it up for
  branch protection. Tags publish GitHub Releases (see above).
