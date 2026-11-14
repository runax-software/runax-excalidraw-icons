# excalidraw-icons

Miro-style Excalidraw libraries (64px icon + editable label below, grouped) built from official icon sets.

| Pack | Icons | Source |
|---|---|---|
| `aws` | 810 | [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/), July 2026 release |
| `azure` | 645 | [Azure Architecture Icons](https://learn.microsoft.com/azure/architecture/icons/), V25 |
| `k8s` | 39 | [kubernetes/community `icons/svg`](https://github.com/kubernetes/community/tree/c8b1af836bc44adbafe45653ceb1a4a54ab14d9a/icons/svg) |
| `techno` | 116 | Hand-picked technology logos |

## Layout

```
build_icon_libraries.py
icons/<pack>/        SVGs used for each library (committed)
downloads/           raw packages (git-ignored)
libraries/           generated .excalidrawlib + .excalidraw (git-ignored)
```

## Build

```sh
python3 build_icon_libraries.py
```

No dependencies beyond Python 3. Each pack is built from its package in `downloads/` if present
(newest wins), otherwise from `icons/<pack>/`.

To update a pack, drop the new package into `downloads/` and rerun:

- `aws`: `Icon-package_*.zip`
- `azure`: `Azure_Public_Service_Icons_*.zip`
- `k8s`: `kubernetes-icons/` (the repo's `icons/` folder)
- `techno`: `techno/` (flat folder of SVGs)

The script keeps only the largest size of each icon, prefers unlabeled variants, and skips
white-only icons (AWS `_Dark` variants), which are invisible on a white canvas.

## Using the libraries

excalidraw.com doesn't store images in library files, so library icons show as empty boxes
unless the drawing already contains them. For each pack:

1. Open `libraries/<pack>-miro-style.excalidraw`, or paste icons from it into your drawing.
2. Import `libraries/<pack>-miro-style.excalidrawlib` from the library panel.

Library items use the same image IDs as the scene, so they render once the scene's images are loaded.

## Licensing

AWS and Microsoft icons may be used in architecture diagrams and documentation under their
terms; Kubernetes icons are open-licensed; technology logos are their owners' trademarks.
Keep this repo private.
