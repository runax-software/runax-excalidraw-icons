"""The `runax-icons` command line. Commands only parse arguments and print: the work is done
by Workspace, Importer, PackBuilder, Validator, IconCatalog and Diagram."""

import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Annotated

import typer

from .download import DownloadError
from .excalidraw import Diagram, DiagramError, ElementFactory, Point
from .excalidraw.guidelines import MANUAL_RULES, Guidelines, LibraryFile
from .packs import ConfigError, Importer, PackBuilder, UpstreamError, Validator
from .workspace import AmbiguousIcon, Workspace, WorkspaceError

app = typer.Typer(
    help="Miro-style Excalidraw icon libraries: build packs and add their icons to diagrams.",
    no_args_is_help=True,
    add_completion=False,
)

PackNames = Annotated[
    list[str] | None, typer.Argument(help="Packs to use (default: all).", show_default=False)
]
PackOption = Annotated[str | None, typer.Option("--pack", "-p", help="Only look in this pack.")]


@app.callback()
def main(
    ctx: typer.Context,
    root: Annotated[Path, typer.Option(help="Folder holding the packs.")] = Path("."),
) -> None:
    ctx.obj = Workspace(root.resolve())


@app.command()
def build(ctx: typer.Context, packs: PackNames = None) -> None:
    """Build each pack's library, scene and README from its src/ (no network)."""
    with _errors():
        _build(ctx.obj, packs)


@app.command("import")
def import_(ctx: typer.Context, packs: PackNames = None) -> None:
    """Download each pack's `import:` entries into src/, then build."""
    with _errors():
        for pack in ctx.obj.packs(packs):
            Importer(pack, log=typer.echo).run()
        _build(ctx.obj, packs)


@app.command()
def check(ctx: typer.Context, packs: PackNames = None) -> None:
    """Report pack problems without building; exit 1 if there are any."""
    with _errors():
        problems = [p for pack in ctx.obj.packs(packs) for p in Validator(pack).problems()]

    for problem in problems:
        typer.echo(str(problem), err=True)
    if problems:
        raise typer.Exit(1)
    typer.echo("no problems")


@app.command()
def guidelines(
    ctx: typer.Context,
    packs: PackNames = None,
    publishable: Annotated[
        bool, typer.Option(help="Only packs with `publish: true` in pack.yml (what CI enforces).")
    ] = False,
) -> None:
    """Check built libraries against the libraries.excalidraw.com submission guidelines."""
    with _errors():
        selected = [p for p in ctx.obj.packs(packs) if p.config.publish or not publishable]

    failed = False
    for pack in selected:
        if not pack.library_path.exists():
            typer.echo(f"[{pack.name}] not built: run `runax-icons build {pack.name}`", err=True)
            failed = True
            continue

        findings = Guidelines().check(LibraryFile(pack.library_path))
        typer.echo(f"[{pack.name}] " + ("follows the guidelines" if not findings else f"{len(findings)} problems"))
        for finding in findings:
            typer.echo(f"  {finding}", err=True)
        failed = failed or bool(findings)

    if selected:
        typer.echo("Check by hand: " + "; ".join(MANUAL_RULES))
    if failed:
        raise typer.Exit(1)


@app.command()
def search(
    ctx: typer.Context,
    text: Annotated[str, typer.Argument(help="Part of a label or file name; empty lists every icon.")] = "",
    pack: PackOption = None,
) -> None:
    """Find icons by label or file name across packs."""
    with _errors():
        matches = ctx.obj.catalog(pack).search(text)

    for m in matches:
        typer.echo(f"{m.pack.name:<14} {m.label:<40} {m.pack.name}/src/{m.icon.path.as_posix()}")
    if not matches:
        typer.echo(f"no icons match {text!r}", err=True)
        raise typer.Exit(1)


@app.command()
def add(
    ctx: typer.Context,
    diagram: Annotated[Path, typer.Argument(help=".excalidraw file; created if it doesn't exist.")],
    icon: Annotated[str, typer.Argument(help='Icon label, e.g. "Amazon S3" (see `search`).')],
    at: Annotated[
        tuple[float, float] | None,
        typer.Option(help="Top-left position X Y (default: right of the drawing)."),
    ] = None,
    label: Annotated[str | None, typer.Option(help="Caption (default: the icon's label).")] = None,
    pack: PackOption = None,
) -> None:
    """Add an icon with its label to a diagram, embedding its image."""
    with _errors():
        match = ctx.obj.catalog(pack).resolve(icon)
        scene = Diagram(diagram, ElementFactory(_now()))
        placed = scene.add_icon(
            match.icon, label or match.label, Point(*at) if at else None, match.pack.box(match.icon)
        )
        scene.save()

    typer.echo(f"added {label or match.label!r} from {match.pack.name} at {placed.x:g}, {placed.y:g}")


@app.command()
def connect(
    diagram: Annotated[
        Path, typer.Argument(help=".excalidraw file holding both icons.", exists=True, dir_okay=False)
    ],
    source: Annotated[str, typer.Argument(help="Label of the icon the arrow starts at.")],
    target: Annotated[str, typer.Argument(help="Label of the icon the arrow points to.")],
    label: Annotated[str | None, typer.Option(help='Text on the arrow, e.g. "HTTPS".')] = None,
    dashed: Annotated[bool, typer.Option(help="Dashed line, e.g. for async or optional flows.")] = False,
    color: Annotated[str, typer.Option(help="Line color.")] = "#1e1e1e",
) -> None:
    """Draw an arrow between two icons in a diagram, bound to both so it follows them."""
    with _errors():
        scene = Diagram(diagram, ElementFactory(_now()))
        scene.connect(source, target, label, dashed, color)
        scene.save()

    typer.echo(f"connected {source!r} -> {target!r}")


def _build(workspace: Workspace, names: list[str] | None) -> None:
    factory = ElementFactory(_now())
    for pack in workspace.packs(names):
        result = PackBuilder(pack, factory).build()
        typer.echo(f"[{pack.name}] packaged {result.icons} icons -> {pack.library_path.name}")
        for problem in result.problems:
            typer.echo(str(problem), err=True)


@contextmanager
def _errors() -> Iterator[None]:
    """Turn the package's errors into a message and a non-zero exit, without a traceback."""
    try:
        yield
    except AmbiguousIcon as error:
        typer.echo(str(error) + ":", err=True)
        for m in error.candidates[:20]:
            typer.echo(f"  {m.pack.name:<14} {m.label}", err=True)
        raise typer.Exit(1) from error
    except (WorkspaceError, ConfigError, UpstreamError, DownloadError, DiagramError) as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(1) from error


def _now() -> int:
    return int(time.time() * 1000)
