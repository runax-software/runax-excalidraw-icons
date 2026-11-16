# runax-excalidraw-icons

Miro-style icon libraries for [Excalidraw](https://excalidraw.com): every item is a 64px icon
with an editable label below it, grouped together, so architecture diagrams look consistent
without hunting for logos.

| Pack                              | Icons | Source                                                                                                                                                                                  |
| --------------------------------- | ----- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`ai`](ai/)                       | 41    | AI models, inference, frameworks and coding tools ([lobehub/lobe-icons](https://github.com/lobehub/lobe-icons))                                                                         |
| [`aws`](aws/)                     | 810   | [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/), July 2026 release                                                                                                 |
| [`azure`](azure/)                 | 645   | [Azure Architecture Icons](https://learn.microsoft.com/azure/architecture/icons/), V25                                                                                                  |
| [`cloudflare`](cloudflare/)       | 113   | Cloudflare logo and product icons ([cloudflare-docs](https://github.com/cloudflare/cloudflare-docs/tree/production/src/icons))                                                          |
| [`data`](data/)                   | 32    | Databases, streaming and data-pipeline logos                                                                                                                                            |
| [`k8s`](k8s/)                     | 43    | [kubernetes/community `icons/svg`](https://github.com/kubernetes/community/tree/c8b1af836bc44adbafe45653ceb1a4a54ab14d9a/icons/svg), plus Kubernetes, Helm, Argo CD and K3s logos |
| [`networking`](networking/)       | 35    | Service mesh, ingress, CNI, DNS, VPN and API protocols (CNCF artwork and others)                                                                                                        |
| [`observability`](observability/) | 27    | Grafana products and signal icons, OpenTelemetry, Prometheus, .NET Aspire, Seq and PostHog                                                                                              |
| [`supabase`](supabase/)           | 10    | Supabase logo and product icons                                                                                                                                                         |
| [`techno`](techno/)               | 73    | Hand-picked technology logos ([gilbarbara/logos](https://github.com/gilbarbara/logos), [simple-icons](https://github.com/simple-icons/simple-icons))                                                                                                                                                            |

Click a pack to see a preview of its icons, where each one came from, and its license.

## Using the libraries

Download `runax-<pack>.excalidrawlib` and `runax-<pack>.excalidraw` from the
[latest release](https://github.com/runax-software/runax-excalidraw-icons/releases/latest), or
[build them yourself](#building).

excalidraw.com doesn't store images in library files, so library icons show as empty boxes
unless the drawing already contains them. For each pack:

1. Open `runax-<pack>.excalidraw`, or paste icons from it into your drawing, so the images are loaded.
2. Import `runax-<pack>.excalidrawlib` from the library panel.

Library items use the same image IDs as the scene, so they render once the scene's images are
loaded.

Packs marked `publish: true` also come as `runax-<pack>-native.excalidrawlib`: the icons drawn
with Excalidraw's own shapes instead of images, so the library works on its own (and can be
published on libraries.excalidraw.com). The shapes approximate the originals: curves become
short straight segments and gradients a single color. Only packs whose icon terms allow that
are published this way (not AWS or Azure).

## For agents: the published site

`uv run runax-icons export site/` writes a static site of every library, an `index.json` of
every pack, library and icon name, and an `llms.txt` explaining to an AI agent how to put
icons into an `.excalidraw` file. Hosted (on GitHub Pages, say), an agent in any repository
needs nothing else: point it at the site's `llms.txt`, for example in that repository's
`AGENTS.md`, and it fetches the libraries it needs and writes the diagram itself.

## Diagrams from your libraries

Excalidraw's library panel can't keep images, but the `.excalidrawlib` files do: `runax-icons`
reads them, images included, and places their items into `.excalidraw` files, connected by arrows
that stay attached when you move things. Agents use it the same way (see the
`excalidraw-diagrams` skill). Point it at your libraries, published or not, ours or any other:

```sh
export RUNAX_ICONS_LIBRARY=~/libraries/runax-aws.excalidrawlib:~/libraries/runax-data.excalidrawlib
alias runax-icons="uvx --from git+https://github.com/runax-software/runax-excalidraw-icons runax-icons"

runax-icons search postgres                                         # find an icon's label
runax-icons add docs/arch.excalidraw "AWS Lambda" --at 0 0 --label "Order API"
runax-icons add docs/arch.excalidraw "PostgreSQL" --at 220 0
runax-icons connect docs/arch.excalidraw "Order API" PostgreSQL --label SQL
```

`add` creates the diagram if needed and embeds each image, so the file opens anywhere.
`--label` renames the caption; `connect` matches icons by caption and takes `--dashed` and
`--color`. `--library <file>` picks libraries per command instead of the environment variable.
Inside this repository, the commands also work without libraries, straight from the packs.

## Building

### Layout

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
  icon.py, sources.py           Icon (naming, fileId); folder, zip and tar readers
  download.py                   Downloader (temporary folder, parallel)
tests/                          pytest suite
pyproject.toml, uv.lock         package and dependencies, locked
<pack>/
  pack.yml                      title, license, imports, hand-made sources, labels, README samples,
                                native_size (vendor's icon sizes), publish (for libraries.excalidraw.com:
                                also builds runax-<pack>-native.excalidrawlib)
  src/                          the SVGs the pack is built from (committed)
  CHANGELOG.md                  the pack's changes
  runax-<pack>.excalidrawlib    generated library (git-ignored)
  runax-<pack>.excalidraw       generated scene with the images (git-ignored)
  README.md                     generated preview, license and sources of the pack
```

### Build

```sh
uv run runax-icons build             # build every pack from its src/ (no network)
uv run runax-icons build k8s data    # build only these packs
uv run runax-icons import            # first refresh src/ from each pack's `import:` urls
uv run runax-icons check             # report pack problems; exit 1 if there are any
uv run runax-icons export site/      # build, then write the site: libraries, index.json, llms.txt
uv run runax-icons guidelines k8s    # check a built library against the libraries.excalidraw.com rules
uv run pytest && uv run pyright      # tests and type checks
```

Needs [uv](https://docs.astral.sh/uv/), which installs the package and its locked dependencies
into `.venv/` on first run. Every folder with a `pack.yml` is a pack, built from every SVG in
its `src/`.

Files in `src/` are either imported or hand-made. Imports are listed in the pack's
`pack.yml`; `runax-icons import` downloads them into a temporary folder and writes the results to
`src/`, so nothing is cached in the repo:

```yaml
import:
  # An archive (zip or tar) replaces the folder src/<into>/ (default: all of src/) with the
  # largest size of each icon, skipping white-only ones (AWS `_Dark` variants).
  - url: https://github.com/kubernetes/community/archive/<commit>.zip
    path: "community-*/icons"          # optional: folder inside the archive
    into: kubernetes
  # A single SVG (or PNG, wrapped in an SVG) is written to src/<into> after optional edits.
  - url: https://caddyserver.com/resources/images/logo-light.svg
    into: other/caddy.svg
    viewBox: "-2 -2 152 151"           # crop, e.g. to drop a wordmark
  # `names` expands one entry per name, filling {name} (and {src}, for a map) in url and into.
  - url: https://raw.githubusercontent.com/cloudflare/cloudflare-docs/production/src/icons/{name}.svg
    into: "products/{name}.svg"
    fill: "#F38020"                    # paint black / currentColor in this color
    names: [workers, r2, d1]
```

Other edits: `replace: [[old, new], ...]` for text. To move to a new release, change the url
and run `uv run runax-icons import <pack>`.

Hand-made files (drawn, cropped from a PNG, or with no known url) are listed under
`sources:` instead, so every file in `src/` has a recorded origin.

What a pack's icons may be put through is declared in `pack.yml` too, from their terms:

```yaml
forbid:                     # on the pack, or on a single import/sources entry
  edit: Microsoft's terms forbid cropping, recoloring or reshaping the icons
  native: redrawing the icons as native shapes changes their shape
  publish: Microsoft permits the icons only in diagrams, training materials or documentation
```

`edit` covers `fill`, `viewBox` and `replace` on imports, `native` the native-shape library, and
`publish` `publish: true`. The build refuses a forbidden edit or `publish: true` with the
reason, and leaves icons whose entry forbids `native` out of the native library.

Both lists are shown in the pack's README. `build` and `check` report files in `src/` that
neither covers, `sources:` entries that match nothing, imported files missing from `src/` and
README samples that aren't labels. `pack.yml` is validated: unknown keys are errors.

## Contributing

New icons and packs are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

The code (`runax_icons/`) is released under the [MIT License](LICENSE).

The icons are **not** covered by that license. They belong to their owners and keep their own
licenses and terms: [NOTICE.md](NOTICE.md) lists them with copyright notices and our changes,
[LICENSES/](LICENSES/) holds the license texts, and each pack's README quotes its terms:

- **AWS** and **Azure** icons are provided by Amazon and Microsoft for use in architecture
  diagrams and documentation, under [AWS's](https://aws.amazon.com/architecture/icons/) and
  [Microsoft's](https://learn.microsoft.com/azure/architecture/icons/) terms.
- **Kubernetes** resource icons are Apache-2.0 ([kubernetes/community](https://github.com/kubernetes/community));
  **Cloudflare** product icons are CC-BY-4.0 ([cloudflare-docs](https://github.com/cloudflare/cloudflare-docs)).
- Other logos come from the projects themselves or from open collections
  ([lobe-icons](https://github.com/lobehub/lobe-icons) MIT,
  [gilbarbara/logos](https://github.com/gilbarbara/logos) and
  [simple-icons](https://github.com/simple-icons/simple-icons) CC0-1.0,
  [cncf/artwork](https://github.com/cncf/artwork)).

All product names, logos and brands are trademarks of their respective owners. They are used
only to identify those products in diagrams; their use does not imply any affiliation with or
endorsement by them. If you own a mark and want an icon changed or removed, please open an issue.
