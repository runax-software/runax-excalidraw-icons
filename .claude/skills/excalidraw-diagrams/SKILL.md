---
name: excalidraw-diagrams
description: Draw architecture diagrams as .excalidraw files in the runax-excalidraw-icons repository, with its icon packs (AWS, Azure, Kubernetes, Cloudflare, networking, data, observability, AI, Supabase, technology logos) and its runax-icons command line. Use when asked, in this repository, to draw, sketch or diagram a system, an architecture, a data flow or infrastructure.
---

# Excalidraw diagrams from icon libraries

`runax-icons`, this repository's command line, places pack icons into `.excalidraw` files,
connected by arrows that stay attached when the diagram is edited. The diagram embeds every
image, so it opens anywhere.

## Setup

Run it from the repository root with `uv run runax-icons`: it reads the packs directly, no
libraries needed. The command line is for this repository only: don't install it elsewhere or
run it from GitHub. Agents in other repositories use the released libraries as `llms.txt` (the
`index` release) explains.

## Steps

1. **Plan first**: list the components (one icon each) and the arrows between them, each with a
   short label ("HTTPS", "SQL", "events").
2. **Find each icon's exact label**:

   ```sh
   uv run runax-icons search postgres
   uv run runax-icons search lambda
   ```

   Prefer the specific product (`Amazon RDS`) over a generic one. For a concept with no product
   icon, use the closest one (a signal icon like `Logs` or `Metrics`, or `REST API`).
3. **Place the icons on a grid**, left to right in the order data flows, about 220px apart
   horizontally and 220px vertically:

   ```sh
   uv run runax-icons add docs/architecture.excalidraw "Cloudflare Workers" --at 0 0
   uv run runax-icons add docs/architecture.excalidraw "AWS Lambda" --at 220 0 --label "Order API"
   uv run runax-icons add docs/architecture.excalidraw "PostgreSQL" --at 440 0
   ```

   `--label` renames the caption to the component's role while keeping the product's icon.
   Without `--at`, an icon goes right of everything already drawn. The file is created if needed.
4. **Connect them by caption**:

   ```sh
   uv run runax-icons connect docs/architecture.excalidraw "Cloudflare Workers" "Order API" --label HTTPS
   uv run runax-icons connect docs/architecture.excalidraw "Order API" PostgreSQL --label SQL --dashed
   ```

   `--dashed` for asynchronous or optional flows, `--color` to tell flows apart.
5. **Check the result** before calling it done: render or open the file and fix overlapping
   icons or arrows crossing captions by moving icons on the grid.

## Notes

- `connect` matches captions (case-insensitive), so every icon needs a unique caption.
- Arrows bind to an icon's image or main shape and follow it when moved. The runax `-native`
  libraries have an invisible rectangle around each icon for this; other libraries' icons drawn
  only with lines get arrows that aren't bound.
- Vendor terms travel with some icons (AWS, Azure: use as published, keep the service name as
  the caption, don't resize out of proportion): use them for diagrams and documentation only.
- For freeform sketches without product icons (boxes, flows, mind maps), the Excalidraw MCP
  server draws directly; add product icons afterwards with `uv run runax-icons add`.
