# runax-excalidraw-icons

Icon libraries for [Excalidraw](https://excalidraw.com) architecture diagrams: AWS, Azure,
Kubernetes, Cloudflare and 1,800+ more, each a 64px icon with an editable caption, Miro style.

## Quick start

No need to clone anything. Pick how you want to draw:

### In Excalidraw, by hand

1. Open the [releases](https://github.com/runax-software/runax-excalidraw-icons/releases), pick a
   pack (say `aws/v0.1.0`) and download `runax-aws-native.excalidrawlib`.
2. In Excalidraw, open the library panel and import it (*⋯* → *Open*, or drag the file onto the
   canvas).
3. Drag icons from the panel into your drawing. Double-click a caption to rename it.

The `-native` libraries draw each icon with Excalidraw's own shapes, so they work anywhere.
They approximate the originals: curves become short straight segments and gradients a single
color. For the exact images, open `runax-aws.excalidraw` instead and copy icons from it.
(`runax-aws.excalidrawlib` holds the images too, but Excalidraw drops a library's images on
import, so on its own its icons show as empty boxes.)

### With an AI agent

Add this to the `AGENTS.md` (or `CLAUDE.md`) of the repository you want diagrams in:

```md
Diagrams: Excalidraw icons are in the GitHub releases of runax-software/runax-excalidraw-icons;
start with `gh release download index -R runax-software/runax-excalidraw-icons -p llms.txt -O -`.
```

Then ask for a diagram ("draw our architecture in docs/architecture.excalidraw"). The agent
reads [`llms.txt`](https://github.com/runax-software/runax-excalidraw-icons/releases/tag/index),
finds icons by name, downloads only the packs it needs and writes the file. It needs the
[GitHub CLI](https://cli.github.com) (`gh`), logged in.

## Packs

| Pack                              | Icons | What's in it                                                                                                                                                                         |
| --------------------------------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [`ai`](ai/)                       | 41    | AI models, inference, frameworks and coding tools ([lobehub/lobe-icons](https://github.com/lobehub/lobe-icons))                                                                      |
| [`aws`](aws/)                     | 810   | [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/), July 2026 release                                                                                              |
| [`azure`](azure/)                 | 645   | [Azure Architecture Icons](https://learn.microsoft.com/azure/architecture/icons/), V25                                                                                               |
| [`cloudflare`](cloudflare/)       | 113   | Cloudflare logo and product icons ([cloudflare-docs](https://github.com/cloudflare/cloudflare-docs/tree/production/src/icons))                                                       |
| [`data`](data/)                   | 43    | Databases, streaming and data-pipeline logos                                                                                                                                         |
| [`k8s`](k8s/)                     | 43    | [kubernetes/community `icons/svg`](https://github.com/kubernetes/community/tree/c8b1af836bc44adbafe45653ceb1a4a54ab14d9a/icons/svg), plus Kubernetes, Helm, Argo CD and K3s logos |
| [`networking`](networking/)       | 35    | Service mesh, ingress, CNI, DNS, VPN and API protocols (CNCF artwork and others)                                                                                                     |
| [`observability`](observability/) | 27    | Grafana products and signal icons, OpenTelemetry, Prometheus, .NET Aspire, Seq and PostHog                                                                                           |
| [`supabase`](supabase/)           | 10    | Supabase logo and product icons                                                                                                                                                      |
| [`techno`](techno/)               | 73    | Hand-picked technology logos ([gilbarbara/logos](https://github.com/gilbarbara/logos), [simple-icons](https://github.com/simple-icons/simple-icons))                                  |

Click a pack for a preview of its icons, where each one came from, and its terms. Each pack is
released on its own (`aws/v0.1.0`, ...), with its changes in the pack's `CHANGELOG.md`.

## What's in a release

| File                                | What it's for                                                     |
| ----------------------------------- | ----------------------------------------------------------------- |
| `runax-<pack>.excalidraw`           | a drawing with every icon: open it and copy from it               |
| `runax-<pack>.excalidrawlib`        | the exact images, for AI agents                                   |
| `runax-<pack>-native.excalidrawlib` | icons drawn with Excalidraw shapes: for the library panel         |
| `runax-<pack>.json`                 | the pack's icon names and terms, merged into the `index` release  |

The [`index`](https://github.com/runax-software/runax-excalidraw-icons/releases/tag/index)
release lists every pack's latest release in `index.json`, and explains to agents how to use
them in `llms.txt`.

## Using the icons

The icons belong to their owners and keep their terms. In short: use them in diagrams,
documentation and training material, unmodified, with the product name as the caption. AWS and
Azure icons may not be resized out of proportion, recolored or cropped. Each pack's README
quotes its terms.

## Contributing

New icons and packs are welcome: [CONTRIBUTING.md](CONTRIBUTING.md) explains how to build, add
icons and work on the code, and [RELEASING.md](RELEASING.md) how packs are released.

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
