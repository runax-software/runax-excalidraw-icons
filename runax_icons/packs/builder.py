from dataclasses import dataclass, field

from ..excalidraw import ElementFactory, Library, NativeConverter, Scene
from ..excalidraw.elements import LineElement
from ..icon import Icon
from .restrictions import Operation
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
    not_native: list[str] = field(default_factory=list)  # labels left out of the native library (forbidden, or raster)


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
        not_native: list[str] = []
        if self.pack.config.forbid.allows(Operation.NATIVE):
            library, not_native = self._native_library(icons)
            library.save(self.pack.native_library_path)
        self.pack.readme_path.write_text(ReadmeRenderer(self.pack, icons).render(), encoding="utf-8")

        return BuildResult(len(icons), Validator(self.pack, icons).problems(), not_native)

    def _library(self, icons: list[Icon]) -> Library:
        library = Library(self.factory)
        for icon in icons:
            library.add_icon(icon, self.pack.label(icon), self.pack.box(icon))
        return library

    def _native_library(self, icons: list[Icon]) -> tuple[Library, list[str]]:
        """The icons as native shapes, which work on their own in Excalidraw's library panel
        (it drops a library's images), and the labels of those whose `forbid:` rules out
        converting them."""
        self.pack.config.forbid.require(Operation.NATIVE, f"{self.pack.name} native library")
        library = Library(self.factory)
        converter = NativeConverter(self.factory)
        left_out = []
        for icon in icons:
            label = self.pack.label(icon)
            if not self.pack.restrictions(icon).allows(Operation.NATIVE):
                left_out.append(label)
                continue
            elements = converter.icon(icon, label, box=self.pack.box(icon))
            if not any(isinstance(e, LineElement) for e in elements):  # raster icons have no paths
                left_out.append(label)
                continue
            library.add_item(label, elements)
        return library, left_out

    def _scene(self, icons: list[Icon]) -> Scene:
        scene = Scene()
        for i, icon in enumerate(icons):
            col, row = i % SCENE_COLUMNS, i // SCENE_COLUMNS
            scene.add_icon(
                self.factory, icon, self.pack.label(icon), col * SCENE_CELL_W, row * SCENE_CELL_H, self.pack.box(icon)
            )
        return scene
