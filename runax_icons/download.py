import gzip
import hashlib
import zlib
import tempfile
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlparse

import brotli

USER_AGENT = "runax-excalidraw-icons"
WORKERS = 8


class DownloadError(Exception):
    pass


class Downloader:
    """Downloads into a temporary folder that's deleted on exit, so nothing is cached:

        with Downloader() as downloader:
            files = downloader.fetch_all(urls)
    """

    def __enter__(self) -> "Downloader":
        self._folder = tempfile.TemporaryDirectory()
        self.folder = Path(self._folder.name)
        return self

    def __exit__(self, *exc) -> None:
        self._folder.cleanup()

    def fetch_all(self, urls: list[str]) -> dict[str, Path]:
        """Download every distinct url in parallel; url -> file."""
        distinct = list(dict.fromkeys(urls))
        with ThreadPoolExecutor(WORKERS) as pool:
            return dict(zip(distinct, pool.map(self.fetch, distinct)))

    def fetch(self, url: str) -> Path:
        """Download `url` into the folder. Files are prefixed with a hash of the url, so two
        urls ending in the same name (logo.svg) don't overwrite each other."""
        name = PurePosixPath(unquote(urlparse(url).path)).name or "download"
        target = self.folder / f"{hashlib.sha1(url.encode()).hexdigest()[:8]}-{name}"

        headers = {"User-Agent": USER_AGENT, "Accept-Encoding": "gzip, deflate, br"}
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers)) as response:
            encoding = response.headers.get("Content-Encoding", "identity").lower()
            body = response.read()

        # urllib doesn't decode compressed responses, and some servers (grafana.com) compress
        # whatever the request asks for.
        decoders = {"identity": bytes, "gzip": gzip.decompress, "deflate": zlib.decompress, "br": brotli.decompress}
        if encoding not in decoders:
            raise DownloadError(f"{url}: unsupported Content-Encoding {encoding!r}")

        target.write_bytes(decoders[encoding](body))
        return target
