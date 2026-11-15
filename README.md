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
  pack.yml                      title, source, download glob, label overrides, README samples
  icons/                        SVGs used for the library (committed)
  downloads/                    raw packages (git-ignored)
  <pack>.excalidrawlib          generated library (git-ignored)
  <pack>.excalidraw             generated scene with the images (git-ignored)
  README.md                     generated preview of the pack
```

## Build

```sh
uv run build.py
```

Needs [uv](https://docs.astral.sh/uv/), which installs the locked dependencies into `.venv/`
on first run. Every folder with a `pack.yml` is a pack. Each pack is built from its package in `<pack>/downloads/` if
present (newest wins), otherwise from `<pack>/icons/`.

To update a pack, drop the new package into its `downloads/` folder and rerun:

- `ai/downloads/sources/` (URLs in `ai/SOURCES.txt`)
- `aws/downloads/Icon-package_*.zip`
- `azure/downloads/Azure_Public_Service_Icons_*.zip`
- `cloudflare/downloads/sources/` (URLs in `cloudflare/SOURCES.txt`)
- `data/downloads/sources/` (one SVG per product; URLs in `data/SOURCES.txt`)
- `k8s/downloads/sources/kubernetes-icons/` (the repo's `icons/` folder), plus `cncf/` and `other/` logos (URLs in `k8s/SOURCES.txt`)
- `networking/downloads/sources/` (URLs in `networking/SOURCES.txt`)
- `observability/downloads/sources/<vendor>/` (one SVG per product; URLs in `observability/SOURCES.txt`)
- `supabase/downloads/sources/` (URLs in `supabase/SOURCES.txt`)
- `techno/downloads/techno/` (flat folder of SVGs, picked from `svg.zip`)

The script keeps only the largest size of each icon, prefers unlabeled variants, and skips
white-only icons (AWS `_Dark` variants), which are invisible on a white canvas.

## Using the libraries

excalidraw.com doesn't store images in library files, so library icons show as empty boxes
unless the drawing already contains them. For each pack:

1. Open `<pack>/<pack>.excalidraw`, or paste icons from it into your drawing.
2. Import `<pack>/<pack>.excalidrawlib` from the library panel.

Library items use the same image IDs as the scene, so they render once the scene's images are loaded.

## Licensing

AWS and Microsoft icons may be used in architecture diagrams and documentation under their
terms; Kubernetes icons are open-licensed; the other logos (technology, AI, Cloudflare, data, networking, observability, Supabase) are their owners' trademarks.
Keep this repo private.
