from collections.abc import Callable

from ..download import Downloader
from .pack import Pack


class Importer:
    """Refreshes a pack's src/ from its `import:` entries."""

    def __init__(self, pack: Pack, log: Callable[[str], None] = print):
        self.pack = pack
        self.log = log

    def run(self) -> None:
        targets = self.pack.import_targets
        if not targets:
            return

        with Downloader() as downloader:
            downloads = downloader.fetch_all([target.url for target in targets])
            counts = [target.write(downloads[target.url], self.pack.src_dir) for target in targets]

        self.log(f"[{self.pack.name}] imported {sum(counts)} icons from {len(targets)} imports")
