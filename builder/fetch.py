import hashlib
import shutil
import urllib.request
from pathlib import PurePosixPath
from urllib.parse import unquote, urlparse

USER_AGENT = "excalidraw-icons build.py"


def fetch(url, folder):
    """Download `url` into `folder` and return the file. Files are prefixed with a hash of
    the url, so two urls ending in the same name (logo.svg) don't overwrite each other."""
    name = PurePosixPath(unquote(urlparse(url).path)).name or "download"
    target = folder / f"{hashlib.sha1(url.encode()).hexdigest()[:8]}-{name}"
    if target.exists():  # the same url twice in one import
        return target

    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request) as response, open(target, "wb") as out:
        shutil.copyfileobj(response, out)

    return target
