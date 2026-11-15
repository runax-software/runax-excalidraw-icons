# Changelog

All notable changes to the `runax-icons` package and command line, and to the repository, are documented in
this file. Each pack has its own `CHANGELOG.md` for its icons.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
All packs in the repository are released together.

## [Unreleased]

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
- CI, each workflow running only when its files change: `ci` (tests and type checks)
  for the package, `build` (build and check every pack, generated READMEs committed) for packs
  and the build code. `build` also publishes the libraries to a GitHub Release for `v*` tags.
