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
| [`data`](data/)                   | 34    | Databases, streaming and data-pipeline logos                                                                                                                                            |
| [`k8s`](k8s/)                     | 44    | [kubernetes/community `icons/svg`](https://github.com/kubernetes/community/tree/c8b1af836bc44adbafe45653ceb1a4a54ab14d9a/icons/svg), plus Kubernetes, Helm, Argo CD, K3s and K3OS logos |
| [`networking`](networking/)       | 35    | Service mesh, ingress, CNI, DNS, VPN and API protocols (CNCF artwork and others)                                                                                                        |
| [`observability`](observability/) | 27    | Grafana products and signal icons, OpenTelemetry, Prometheus, .NET Aspire, Seq and PostHog                                                                                              |
| [`supabase`](supabase/)           | 10    | Supabase logo and product icons                                                                                                                                                         |
| [`techno`](techno/)               | 80    | Hand-picked technology logos                                                                                                                                                            |

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

## Diagrams from the command line

`runax-icons` puts pack icons into `.excalidraw` files and connects them with arrows that stay
attached when you move things around in Excalidraw:

```sh
uv run runax-icons search postgres                                  # find an icon's label
uv run runax-icons add diagram.excalidraw "Cloudflare Workers" --at 0 0
uv run runax-icons add diagram.excalidraw "PostgreSQL" --at 220 0
uv run runax-icons connect diagram.excalidraw "Cloudflare Workers" PostgreSQL --label SQL
```

`add` creates the diagram if needed and embeds the icon's image, so the file opens anywhere
without the libraries. `--label` renames the caption; `connect` matches icons by caption and
takes `--dashed` and `--color`.

## Building

### Layout

```
runax_icons/                    the `runax-icons` package and command line
  cli.py                        commands (Typer)
  workspace.py                  Workspace (the packs in a folder), IconCatalog (search, resolve)
  packs/                        Pack, PackConfig (pack.yml), import entries, Importer,
                                Validator, PackBuilder, ReadmeRenderer
  svg/                          SvgDocument, edits (Fill, ViewBox, Replace)
  excalidraw/                   typed elements, Scene, Library, Diagram, geometry, guidelines
  icon.py, sources.py           Icon (naming, fileId); folder, zip and tar readers
  download.py                   Downloader (temporary folder, parallel)
tests/                          pytest suite
pyproject.toml, uv.lock         package and dependencies, locked
<pack>/
  pack.yml                      title, license, imports, hand-made sources, labels, README samples,
                                native_size (vendor's icon sizes), publish (for libraries.excalidraw.com)
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
and run `uv run runax-icons import <pack>`. `techno` has no imports: its logos were picked from
a local `svg.zip` (kept in `techno/downloads/`, git-ignored).

Hand-made files (drawn, cropped from a PNG, or with no known url) are listed under
`sources:` instead, so every file in `src/` has a recorded origin.

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
