# excalidraw-icons

Miro-style Excalidraw libraries (64px icon + editable label below, grouped) built from official icon sets.

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

## Layout

```
build.py                        entry point: builds every pack
builder/                        Pack, IconSource, Icon, ExcalidrawExporter, ReadmeRenderer
pyproject.toml, uv.lock         dependencies (PyYAML), locked
<pack>/
  pack.yml                      title, imports, hand-made sources, label overrides, README samples
  src/                          the SVGs the pack is built from (committed)
  runax-<pack>.excalidrawlib    generated library (git-ignored)
  runax-<pack>.excalidraw       generated scene with the images (git-ignored)
  README.md                     generated preview and sources of the pack
```

## Build

```sh
uv run build.py                 # build every pack from its src/ (no network)
uv run build.py k8s data        # build only these packs
uv run build.py --import        # first refresh src/ from each pack's `import:` urls
```

Needs [uv](https://docs.astral.sh/uv/), which installs the locked dependencies into `.venv/`
on first run. Every folder with a `pack.yml` is a pack, built from every SVG in its `src/`.

Files in `src/` are either imported or hand-made. Imports are listed in the pack's
`pack.yml`; `--import` downloads them into a temporary folder and writes the results to
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
and run `uv run build.py --import <pack>`. `techno` has no imports: its logos were picked from
a local `svg.zip` (kept in `techno/downloads/`, git-ignored).

Hand-made files (drawn, cropped from a PNG, or with no known url) are listed under
`sources:` instead, so every file in `src/` has a recorded origin.

Both lists are shown in the pack's README. The build warns about files in `src/` that neither
covers, `sources:` entries that match nothing, and imported files missing from `src/`.

## Using the libraries

excalidraw.com doesn't store images in library files, so library icons show as empty boxes
unless the drawing already contains them. For each pack:

1. Open `<pack>/runax-<pack>.excalidraw`, or paste icons from it into your drawing.
2. Import `<pack>/runax-<pack>.excalidrawlib` from the library panel.

Library items use the same image IDs as the scene, so they render once the scene's images are loaded.

## Licensing

AWS and Microsoft icons may be used in architecture diagrams and documentation under their
terms; Kubernetes icons are open-licensed; the other logos (technology, AI, Cloudflare, data, networking, observability, Supabase) are their owners' trademarks.
Keep this repo private.
