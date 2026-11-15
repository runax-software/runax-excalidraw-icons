# Contributing

Thanks for helping! Icons and packs are plain files plus a `pack.yml`, so most changes need no
code.

## Setup

Install [uv](https://docs.astral.sh/uv/), then from the repo root:

```sh
uv run runax-icons build            # builds every pack into <pack>/runax-<pack>.excalidrawlib
uv run runax-icons build data       # builds one pack
uv run runax-icons check            # reports pack problems
```

## Code changes

The `runax_icons` package is laid out in the [README](README.md#layout) and described class by
class in [AGENTS.md](AGENTS.md#layout). Before opening a pull request:

```sh
uv run pytest       # add a test for new behavior
uv run pyright      # type hints everywhere, `X | None` rather than Optional
```

## AI agents

The repo ships agent tooling through [APM](https://github.com/microsoft/apm): run `apm install`
to deploy the skills in `.claude/skills/` (`icon-packs` covers the steps below,
`excalidraw-diagrams` drawing with the packs), the Excalidraw MCP server in `.mcp.json` and the
Pyright language server in `.lsp.json`. [AGENTS.md](AGENTS.md) is the guide for agents.

## Adding an icon

1. Prefer an official source: the project's own repository or website, or an open collection
   ([gilbarbara/logos](https://github.com/gilbarbara/logos),
   [simple-icons](https://github.com/simple-icons/simple-icons),
   [lobe-icons](https://github.com/lobehub/lobe-icons), [cncf/artwork](https://github.com/cncf/artwork)).
   Use the icon (mark) rather than the full wordmark, in color where one exists.
2. Add an `import:` entry to the pack's `pack.yml` with its url and the target file in `src/`,
   plus any edits it needs (`viewBox` to crop off a wordmark, `fill` to color a single-color icon,
   `replace` for small text fixes). See the [README](README.md#build) for the format.
3. Run `uv run runax-icons import <pack>`, which downloads it into `src/` and builds the pack.
4. If the file name doesn't make a good label, add it under `labels:`. Add it to `samples:` if it
   belongs in the README preview.
5. Check the icon in the pack's generated README or in Excalidraw, run `uv run runax-icons check`,
   and commit `pack.yml`, `src/` and `README.md`.

Files that can't be imported (drawn by hand, cut out of a raster image, no stable url) go in
`src/` directly, with an entry under `sources:` saying where they came from. The build warns
about files in `src/` that no `import:` or `sources:` entry covers.

## Adding a pack

Create `<pack>/pack.yml` with a `title`, `source`, `license` and its `import:` / `sources:`
entries, then run `uv run runax-icons import <pack>`. Every folder with a `pack.yml` is a pack.

## CI

`.github/workflows/ci.yml` runs only what a pull request affects: tests and type checks when
Python code changes, and a build, `check` and guidelines check for each changed pack. The single
`ci` check is green when everything that ran passed. `release.yml` publishes tagged releases.

## Licensing

Only add icons whose license or terms allow redistribution for diagrams, and record that in
the pack's `license`. Product logos are trademarks of their owners: use them unmodified apart
from cropping and coloring, and don't add icons that suggest an endorsement.
