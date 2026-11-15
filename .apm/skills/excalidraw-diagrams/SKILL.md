---
name: excalidraw-diagrams
description: Draw architecture diagrams in Excalidraw with the runax icon packs (AWS, Azure, Kubernetes, Cloudflare, networking, data, observability, AI, Supabase, technology logos). Use when asked to draw, sketch or diagram a system, an architecture, a data flow or infrastructure as an .excalidraw file.
---

# Excalidraw diagrams with the runax icon packs

`runax-icons` puts real product icons into `.excalidraw` files and connects them with arrows
that stay attached when the diagram is edited. Run it from the repo root with `uv run`.

## Steps

1. **Plan the boxes and flows first**: list the components (one icon each) and the arrows
   between them, with a short label per arrow ("HTTPS", "SQL", "events").
2. **Find each icon's label**:

   ```sh
   uv run runax-icons search postgres            # pack, label, file
   uv run runax-icons search lambda --pack aws
   ```

   Use the exact label from the output. Prefer the specific product (`Amazon RDS`) over a
   generic one; for a concept with no product icon, use the closest signal icon
   (`Logs`, `Metrics`, `Traces`, `Alerts`, `Dashboards` in observability) or `REST API`.
3. **Place the icons on a grid**, left to right in the order data flows, about 200px apart
   horizontally and 220px vertically (icons are 64px with a caption below):

   ```sh
   uv run runax-icons add diagram.excalidraw "Cloudflare Workers" --at 0 0
   uv run runax-icons add diagram.excalidraw "PostgreSQL" --at 220 0
   uv run runax-icons add diagram.excalidraw "Redis" --at 220 220
   uv run runax-icons add diagram.excalidraw "AWS Lambda" --at 0 0 --label "Order API"
   ```

   `--label` renames the caption (the component's role) while keeping the product's icon.
   Without `--at`, an icon goes right of everything already drawn.
4. **Connect them by caption**:

   ```sh
   uv run runax-icons connect diagram.excalidraw "Cloudflare Workers" PostgreSQL --label SQL
   uv run runax-icons connect diagram.excalidraw "Cloudflare Workers" Redis --label cache --dashed
   ```

   Use `--dashed` for asynchronous or optional flows, `--color` to tell flows apart.
5. **Check the result** before calling it done: open the file in Excalidraw, or render it, and
   fix overlapping icons or arrows crossing captions by moving icons on the grid.

## Notes

- Captions are what `connect` matches (case-insensitive), so give every icon a unique caption.
- The icons' images are embedded in the diagram, so it opens anywhere without the libraries.
- For freeform sketches without product icons (boxes, flows, mind maps), the Excalidraw MCP
  server (`excalidraw` in `.mcp.json`) draws directly; add product icons afterwards with
  `runax-icons add`.
