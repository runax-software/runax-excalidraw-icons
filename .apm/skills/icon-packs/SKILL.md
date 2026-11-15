---
name: icon-packs
description: Add, fix or remove icons and packs in runax-excalidraw-icons. Use when asked to add an icon or logo, add a pack, change a label, recolor or crop an icon, update an icon set to a new release, or when `uv run runax-icons build` warns about sources.
---

# Icon packs

Every folder with a `pack.yml` is a pack. It is built from the SVGs in its `src/` into
`runax-<pack>.excalidrawlib` (library), `runax-<pack>.excalidraw` (scene holding the images) and
a generated `README.md`. Never edit a pack's `README.md` by hand: edit `pack.yml` and rebuild.

## Adding an icon

1. Find an official source, in this order: the project's own repository or website (its logo
   or brand-assets page), then [cncf/artwork](https://github.com/cncf/artwork) for CNCF
   projects, [lobe-icons](https://github.com/lobehub/lobe-icons) for AI brands,
   [gilbarbara/logos](https://github.com/gilbarbara/logos) or
   [simple-icons](https://github.com/simple-icons/simple-icons) (single-color, needs `fill`).
   Prefer the icon/mark over a wordmark, and the color version. Use raw file URLs
   (`raw.githubusercontent.com/...`), not GitHub `blob/` pages.
2. Add an `import:` entry to the pack's `pack.yml`:

   ```yaml
   import:
     - url: https://raw.githubusercontent.com/cncf/artwork/main/projects/istio/icon/color/istio-icon-color.svg
       into: "cncf/istio.svg"          # file in src/; its name becomes the label
       viewBox: "0 0 105 118"          # optional: crop, e.g. to drop a wordmark
       fill: "#169BD6"                 # optional: paint black/currentColor (single-color icons)
       replace: [["old", "new"]]       # optional: text edits
       note: "mark only"               # optional: shown in the README's Sources table
   ```

   Many icons from one place: `names: [a, b]` (or a map of name -> upstream name) with `{name}`
   and `{src}` in `url` and `into`. Archives (zip/tar) use `into: <folder>` and optional
   `path: "<glob of a folder inside>"`; they keep the largest size of each icon.
3. Run `uv run runax-icons import <pack>`. It downloads into a temporary folder, writes `src/`
   and builds. Fix any problem it prints (`pack.yml` is validated: a typo in a key is an error).
4. Look at the result: a crop or color mistake is only visible rendered. Open the pack's
   README preview, or render the icon (e.g. to PNG) and look at it, before calling it done.
5. If the file name doesn't make a good label (`dbt` → "Dbt"), add it under `labels:`
   (lowercased file name without extension → label). Add the label to `samples:` if it belongs
   in the README preview (24 at most).
6. Add a line to the pack's `CHANGELOG.md` under `## [Unreleased]`.

Files that can't be imported (drawn by hand, cut out of a raster image, no stable URL) go in
`src/` directly, with a `sources:` entry (`files` glob, `url`, `note`).

## Rules

- `uv run runax-icons check` must print `no problems`: every file in `src/` is covered by an
  `import:` or `sources:` entry, no `sources:` entry is unused, no imported file is missing,
  every README sample is a label.
- Keep icons as downloaded apart from declared edits: imports are reproduced byte for byte, and
  `.gitattributes` / `.editorconfig` deliberately leave SVG line endings alone.
- Logos are trademarks: crop and color only, never redraw a product's logo. Record the license
  or terms in the pack's `license:`.
- Labels use the product's own spelling and casing (`PostgreSQL`, `gRPC`, `NGINX`), and
  vendor-prefixed names where a bare name would be ambiguous across packs (`Cloudflare Workers`,
  `Supabase Database`).
- One icon per product per repo: if a logo moves to another pack, remove it from the old one.

## Adding a pack

Create `<pack>/pack.yml` with `title`, `source` (markdown, completes "N icons from ..."),
`license`, `import:` and/or `sources:`, `labels:` and `samples:`; add a `CHANGELOG.md`; run
`uv run runax-icons import <pack>`; add the pack to the table in the root `README.md`.
