---
name: excalidraw-diagrams
description: Draw architecture diagrams as .excalidraw files using Excalidraw icon libraries (.excalidrawlib), such as the runax packs (AWS, Azure, Kubernetes, Cloudflare, networking, data, observability, AI, Supabase, technology logos). Use when asked to draw, sketch or diagram a system, an architecture, a data flow or infrastructure.
---

# Excalidraw diagrams from icon libraries

`runax-icons` reads `.excalidrawlib` files, including the images that Excalidraw's own library
panel can't keep, and places their items into `.excalidraw` files, connected by arrows that stay
attached when the diagram is edited. The diagram embeds every image, so it opens anywhere.

## Setup

Which libraries to use comes from `RUNAX_ICONS_LIBRARY` (paths separated by `:`), or from
`--library <file>` on each command. If neither is set, ask the user where their libraries are.

Run the tool with `runax-icons` if it's installed, otherwise straight from GitHub:

```sh
uvx --from git+https://github.com/runax-software/runax-excalidraw-icons runax-icons --help
```

(Inside the runax-excalidraw-icons repository, `uv run runax-icons` also works without libraries:
it reads the packs directly.)

## Steps

1. **Plan first**: list the components (one icon each) and the arrows between them, each with a
   short label ("HTTPS", "SQL", "events").
2. **Find each icon's exact label**:

   ```sh
   runax-icons search postgres
   runax-icons search lambda
   ```

   Prefer the specific product (`Amazon RDS`) over a generic one. For a concept with no product
   icon, use the closest one (a signal icon like `Logs` or `Metrics`, or `REST API`).
3. **Place the icons on a grid**, left to right in the order data flows, about 220px apart
   horizontally and 220px vertically:

   ```sh
   runax-icons add docs/architecture.excalidraw "Cloudflare Workers" --at 0 0
   runax-icons add docs/architecture.excalidraw "AWS Lambda" --at 220 0 --label "Order API"
   runax-icons add docs/architecture.excalidraw "PostgreSQL" --at 440 0
   ```

   `--label` renames the caption to the component's role while keeping the product's icon.
   Without `--at`, an icon goes right of everything already drawn. The file is created if needed.
4. **Connect them by caption**:

   ```sh
   runax-icons connect docs/architecture.excalidraw "Cloudflare Workers" "Order API" --label HTTPS
   runax-icons connect docs/architecture.excalidraw "Order API" PostgreSQL --label SQL --dashed
   ```

   `--dashed` for asynchronous or optional flows, `--color` to tell flows apart.
5. **Check the result** before calling it done: render or open the file and fix overlapping
   icons or arrows crossing captions by moving icons on the grid.

## Notes

- `connect` matches captions (case-insensitive), so every icon needs a unique caption.
- Arrows bind to an icon's image or main shape and follow it when moved; icons drawn only with
  lines (native-shape libraries) get arrows that aren't bound.
- Vendor terms travel with some icons (AWS, Azure: use as published, keep the service name as
  the caption, don't resize out of proportion): use them for diagrams and documentation only.
- For freeform sketches without product icons (boxes, flows, mind maps), the Excalidraw MCP
  server draws directly; add product icons afterwards with `runax-icons add`.
