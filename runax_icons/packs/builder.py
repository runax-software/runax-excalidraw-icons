from dataclasses import dataclass

from ..excalidraw import ElementFactory, Library, Scene
from ..icon import Icon
from .pack import Pack
from .renderer import ReadmeRenderer
from .validator import Problem, Validator

SCENE_COLUMNS = 12
SCENE_CELL_W = 160
SCENE_CELL_H = 150


@dataclass(frozen=True)
class BuildResult:
    icons: int
    problems: list[Problem]


class PackBuilder:
    """Writes a pack's library, its scene (every icon on a grid, with the images) and its README."""

    def __init__(self, pack: Pack, factory: ElementFactory):
        self.pack = pack
        self.factory = factory

    def build(self) -> BuildResult:
        icons = self.pack.icons()
        if not icons:
            return BuildResult(0, [Problem(self.pack.name, f"no icons in {self.pack.name}/src/")])

        self._library(icons).save(self.pack.library_path)
        self._scene(icons).save(self.pack.scene_path, indent=None)
        self.pack.readme_path.write_text(ReadmeRenderer(self.pack, icons).render(), encoding="utf-8")

        return BuildResult(len(icons), Validator(self.pack, icons).problems())

    def _library(self, icons: list[Icon]) -> Library:
        library = Library(self.factory)
        for icon in icons:
            library.add_icon(icon, self.pack.label(icon), self.pack.box(icon))
        return library

    def _scene(self, icons: list[Icon]) -> Scene:
        scene = Scene()
        for i, icon in enumerate(icons):
            col, row = i % SCENE_COLUMNS, i // SCENE_COLUMNS
            scene.add_icon(
                self.factory, icon, self.pack.label(icon), col * SCENE_CELL_W, row * SCENE_CELL_H, self.pack.box(icon)
            )
        return scene
