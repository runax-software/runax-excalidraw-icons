# Releasing

Each pack is released on its own, tagged `<pack>/vX.Y.Z` (`aws/v0.1.0`, `k8s/v1.2.0`). The
release workflow (`.github/workflows/release.yml`) builds the pack, attaches its files to the
release, and refreshes the `index` release that agents read. Nothing is published to
libraries.excalidraw.com.

## Versions

Semantic Versioning, per pack:

- **Major**: icons removed or renamed (their label changed), so diagrams or agents that look
  them up by name break.
- **Minor**: icons added, or a new source release of the same icons.
- **Patch**: fixes that keep every label: a corrected color, crop or caption wrap.

## Releasing a pack

1. **Write the notes.** In the pack's `CHANGELOG.md`, rename `## [Unreleased]` to the version and
   date, and add a new empty `Unreleased` above it:

   ```md
   ## [Unreleased]

   ## [0.1.0] - 2026-11-16

   ### Added
   ...
   ```

   Commit and push this to `main` first: the release is built from the tagged commit, and fails
   if its changelog has no section for the version.

2. **Tag it**, either way:

   - **GitHub UI**: Releases → *Draft a new release* → *Choose a tag* → type `aws/v0.1.0` →
     *Create new tag on publish*, target `main`. Leave the title and notes empty to use the
     changelog section (or write your own: they are kept). Untick *Set as the latest release*,
     then *Publish release*.
   - **Command line**:

     ```sh
     git tag aws/v0.1.0
     git push origin aws/v0.1.0
     ```

3. **Check the run** in Actions (*release*). When it's green, the release has:

   | File | What |
   |---|---|
   | `runax-<pack>.excalidrawlib` | the library |
   | `runax-<pack>.excalidraw` | a scene with every icon, images included |
   | `runax-<pack>-native.excalidrawlib` | native-shape library (`publish: true` packs only) |
   | `runax-<pack>.json` | the pack's entry for `index.json` |
   | `NOTICE.md`, `LICENSE`, `LICENSES/*` | notices and license texts |

   and the `index` release's `index.json` and `llms.txt` list the new version.

Several packs can be released at once (one tag each); index refreshes run one at a time and
each includes every pack's latest release.

## The index release

`index` is a fixed release whose files are replaced on every pack release: `index.json` (each
pack's latest release, terms and icon names) and `llms.txt` (how agents download and use them).
Only plain `X.Y.Z` versions count as latest; pre-releases like `aws/v1.0.0-rc.1` are released
but not indexed.

To rebuild it without releasing a pack (after deleting a release, say): Actions → *release* →
*Run workflow*.

## The command line

A plain `vX.Y.Z` tag releases the `runax-icons` command line, with notes generated from the
merged pull requests and no icon files. Its changes are in the root `CHANGELOG.md`.

## Trying a release locally

```sh
uv run runax-icons release aws/v0.1.0 --out dist --notes dist/notes.md   # the pack's assets
uv run runax-icons index dist --repo runax-software/runax-excalidraw-icons --out dist/index
```

## When a release fails

- **"has no `## [X.Y.Z]` section"**: the changelog on the tagged commit lacks the version. Delete
  the release and the tag (`gh release delete aws/v0.1.0 --cleanup-tag`), push the changelog,
  and release again.
- **`check` failed**: fix the pack on `main`, then delete and recreate the release the same way.
- **A file is missing or wrong on a release**: re-run the workflow run; files are replaced, not
  duplicated.
