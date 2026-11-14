import uuid

SOURCE = "https://excalidraw.com"
ICON_SIZE = 64
LABEL_Y = 72
FONT_SIZE = 14
LINE_HEIGHT = 1.25
FONT_FAMILY = 2  # Helvetica
CHAR_WIDTH = FONT_SIZE * 0.55  # average Helvetica glyph width estimate
MAX_LINE_CHARS = 18  # wrap labels Miro-style instead of one very wide line
SCENE_COLUMNS = 12
SCENE_CELL_W = 160
SCENE_CELL_H = 150


class ExcalidrawExporter:
    """Excalidraw library and scene JSON for (icon, label) pairs. Each item is the icon
    with its label below, grouped together.

    excalidraw.com's library format has no place for binary files: library items reference
    their SVG by `fileId`, and the SVG data is also written to a top-level `files` map, but
    excalidraw.com ignores that map on import. The scene embeds the same files under the same
    (deterministic) fileIds, so library items render once the scene's images are loaded.
    """

    def __init__(self, now):
        self.now = now  # unix ms, stamped on every element and file

    @staticmethod
    def wrap_label(label):
        lines, current = [], ""

        for word in label.split(" "):
            candidate = f"{current} {word}".strip()

            if current and len(candidate) > MAX_LINE_CHARS:
                lines.append(current)
                current = word
            else:
                current = candidate
        if current:
            lines.append(current)

        return "\n".join(lines)

    @staticmethod
    def _rand_id():
        return uuid.uuid4().hex[:20]

    @staticmethod
    def _rand_int():
        return uuid.uuid4().int & 0x7FFFFFFF

    def library(self, items):
        return {
            "type": "excalidrawlib",
            "version": 2,
            "source": SOURCE,
            "libraryItems": [
                {
                    "id": self._rand_id(),
                    "status": "unpublished",
                    "elements": self._item(icon, label),
                    "created": self.now,
                    "name": label,
                }
                for icon, label in items
            ],
            "files": self._files(
                items
            ),  # ignored by excalidraw.com; see class docstring
        }

    def scene(self, items):
        elements = []
        for i, (icon, label) in enumerate(items):
            col, row = i % SCENE_COLUMNS, i // SCENE_COLUMNS
            elements += self._item(icon, label, col * SCENE_CELL_W, row * SCENE_CELL_H)

        return {
            "type": "excalidraw",
            "version": 2,
            "source": SOURCE,
            "elements": elements,
            "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None},
            "files": self._files(items),
        }

    def _files(self, items):
        return {
            icon.file_id: {
                "mimeType": "image/svg+xml",
                "id": icon.file_id,
                "dataURL": icon.data_url,
                "created": self.now,
                "lastRetrieved": self.now,
            }
            for icon, _ in items
        }

    def _item(self, icon, label, ox=0, oy=0):
        group_id = self._rand_id()

        image = self._element("image", ox, oy, ICON_SIZE, ICON_SIZE, group_id)
        image.update(
            {"status": "saved", "fileId": icon.file_id, "scale": [1, 1], "crop": None}
        )

        text = self.wrap_label(label)
        lines = text.split("\n")
        width = round(max(len(line) for line in lines) * CHAR_WIDTH, 2)
        height = round(len(lines) * FONT_SIZE * LINE_HEIGHT, 2)
        caption = self._element(
            "text",
            ox + ICON_SIZE / 2 - width / 2,
            oy + LABEL_Y,
            width,
            height,
            group_id,
        )

        caption.update(
            {
                "strokeColor": "#1e1e1e",
                "text": text,
                "originalText": text,
                "fontSize": FONT_SIZE,
                "fontFamily": FONT_FAMILY,
                "textAlign": "center",
                "verticalAlign": "top",
                "containerId": None,
                "autoResize": True,
                "lineHeight": LINE_HEIGHT,
                "baseline": round(FONT_SIZE * 0.88),
            }
        )

        return [image, caption]

    def _element(self, kind, x, y, width, height, group_id):
        return {
            "id": self._rand_id(),
            "type": kind,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "angle": 0,
            "strokeColor": "transparent",
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 1,
            "strokeStyle": "solid",
            "roughness": 0,
            "opacity": 100,
            "groupIds": [group_id],
            "frameId": None,
            "roundness": None,
            "seed": self._rand_int(),
            "version": 1,
            "versionNonce": self._rand_int(),
            "isDeleted": False,
            "boundElements": None,
            "updated": self.now,
            "link": None,
            "locked": False,
        }
