#!/usr/bin/env python3
"""Package icon sets as Miro-style Excalidraw libraries.

Layout (relative to this script):

  downloads/   raw packages, as downloaded (zip files or folders)
  icons/       per pack, exactly the SVGs that went into its library
  libraries/   <pack>-miro-style.excalidrawlib and <pack>-miro-style.excalidraw

Packs and where their downloads come from:

  aws    downloads/Icon-package_*.zip                https://aws.amazon.com/architecture/icons/
  azure  downloads/Azure_Public_Service_Icons_*.zip  https://learn.microsoft.com/azure/architecture/icons/
  k8s    downloads/kubernetes-icons/                 https://github.com/kubernetes/community/tree/main/icons/svg
  techno downloads/techno/                          technology logos

The newest matching download wins. Without a download, a pack is rebuilt from icons/<pack>/.

Each library item is a 64x64 image plus an editable label below it, grouped together.
Only the largest size of each icon is kept (unlabeled variants preferred), and white-only
icons (AWS `_Dark` variants, meant for dark backgrounds) are skipped because they are
invisible on a white canvas.

Note: excalidraw.com's library format has no place for binary files. Library items
reference their SVG by `fileId`, and the SVG data is also written to a top-level
`files` map, but excalidraw.com ignores that map on import. The companion `.excalidraw`
scene embeds the same files under the same (deterministic) fileIds. Open that scene
first, or copy icons from it, so the images render.
"""

import base64
import json
import re
import shutil
import time
import uuid
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent
DOWNLOADS = ROOT / "downloads"
ICONS = ROOT / "icons"
LIBRARIES = ROOT / "libraries"

# kubernetes/community names files by kubectl short name.
K8S_LABELS = {
    "api": "API Server", "c-c-m": "Cloud Controller Manager", "c-m": "Controller Manager",
    "k-proxy": "Kube Proxy", "kubelet": "Kubelet", "sched": "Scheduler",
    "control-plane": "Control Plane", "etcd": "etcd", "node": "Node",
    "c-role": "ClusterRole", "cm": "ConfigMap", "crb": "ClusterRoleBinding",
    "crd": "CustomResourceDefinition", "cronjob": "CronJob", "deploy": "Deployment",
    "ds": "DaemonSet", "ep": "Endpoints", "group": "Group", "hpa": "HorizontalPodAutoscaler",
    "ing": "Ingress", "job": "Job", "limits": "LimitRange", "netpol": "NetworkPolicy",
    "ns": "Namespace", "pod": "Pod", "psp": "PodSecurityPolicy", "pv": "PersistentVolume",
    "pvc": "PersistentVolumeClaim", "quota": "ResourceQuota", "rb": "RoleBinding",
    "role": "Role", "rs": "ReplicaSet", "sa": "ServiceAccount", "sc": "StorageClass",
    "secret": "Secret", "sts": "StatefulSet", "svc": "Service", "user": "User", "vol": "Volume",
}

# Typos in the logo file names.
TECHNO_LABELS = {"cosmos-bd": "Cosmos DB", "playwrite": "Playwright", "postgressql": "PostgreSQL"}

PACKS = {
    "aws": {"download": "Icon-package_*.zip"},
    "azure": {"download": "Azure_Public_Service_Icons_*.zip"},
    "k8s": {"download": "kubernetes-icons", "labels": K8S_LABELS},
    "techno": {"download": "techno", "labels": TECHNO_LABELS},
}

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

# Stable namespace so the same SVG content always gets the same fileId across runs.
FILE_ID_NAMESPACE = uuid.UUID("6f1c3c3e-4f0a-4c39-9a51-0d2b1f3e8a77")

PREFIX_RE = re.compile(r"^(?:Arch(?:-Category)?_|Res_|\d+\s*-icon-service-)", re.IGNORECASE)
SIZE_SUFFIX_RE = re.compile(r"[_-](\d{2,3})(?:@\dx)?(?=(?:[_-](?:Light|Dark))?$)")  # _48, _48_Dark
SIZE_DIR_RE = re.compile(r"^\d{2,3}$")
LIGHT_RE = re.compile(r"[_-]Light$", re.IGNORECASE)
COLOR_RE = re.compile(r'(?:fill|stroke|stop-color)\s*[=:]\s*"?\s*(#[0-9a-f]{3,8}|[a-z]+)', re.IGNORECASE)
SHAPE_RE = re.compile(r"<(?:path|rect|circle|ellipse|polygon|polyline|line|text)\b([^>]*)>", re.IGNORECASE)
GROUP_FILL_RE = re.compile(r'<(?:svg|g)\b[^>]*\bfill\s*[=:]\s*"?\s*(?!none)[#a-z]', re.IGNORECASE)
WHITE = {"#fff", "#ffffff", "white"}
NO_PAINT = {"none", "transparent", "currentcolor", "inherit"}


def rand_id():
    return uuid.uuid4().hex[:20]


def rand_int():
    return uuid.uuid4().int & 0x7FFFFFFF


def icon_size(path):
    """Resolution of an icon from its filename suffix (_64) or size folder (64/)."""
    m = SIZE_SUFFIX_RE.search(path.stem)
    if m:
        return int(m.group(1))
    for part in reversed(path.parent.parts):
        if SIZE_DIR_RE.match(part):
            return int(part)
    return 0


def dedupe_key(path):
    """Identity of an icon regardless of which resolution variant it is."""
    return re.sub(r"\s+", "", SIZE_SUFFIX_RE.sub("", path.stem)).lower()


def clean_label(stem, labels):
    name = SIZE_SUFFIX_RE.sub("", stem)
    if name.lower() in labels:
        return labels[name.lower()]
    name = LIGHT_RE.sub("", name)  # its white `_Dark` twin is skipped, so the suffix is noise
    name = PREFIX_RE.sub("", name)
    words = [w for w in re.split(r"[-_\s]+", name) if w]
    # Capitalize the first letter only, so acronyms like EC2 / IoT / VPN survive.
    return " ".join(w[:1].upper() + w[1:] for w in words)


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


def is_white_only(svg):
    text = svg.decode("utf-8", errors="ignore")
    painted = {c.lower() for c in COLOR_RE.findall(text)} - NO_PAINT
    if not painted or not painted <= WHITE:
        return False
    # A shape without its own fill renders black unless a parent group sets one.
    unfilled = any("fill" not in attrs for attrs in SHAPE_RE.findall(text))
    return not unfilled or bool(GROUP_FILL_RE.search(text))


def iter_svgs(source):
    """(relative path, svg bytes) for every SVG in a zip file or folder."""
    if source.is_dir():
        for path in sorted(source.rglob("*.svg")):
            yield PurePosixPath(path.relative_to(source).as_posix()), path.read_bytes()
        return
    with zipfile.ZipFile(source) as archive:
        for info in archive.infolist():
            path = PurePosixPath(info.filename)
            # __MACOSX/._*.svg entries are Finder metadata, not icons.
            if "__MACOSX" in path.parts or path.name.startswith("._") or path.suffix.lower() != ".svg":
                continue
            yield path, archive.read(info)


def collect_icons(source, labels):
    """Pick the best variant of each icon: largest size, unlabeled over labeled."""
    best = {}
    for path, svg in iter_svgs(source):
        if is_white_only(svg):
            continue
        key = dedupe_key(path)
        rank = (icon_size(path), "unlabeled" in path.parts)
        if key not in best or rank > best[key][0]:
            best[key] = (rank, path, svg)
    return sorted(((p, svg) for _, p, svg in best.values()), key=lambda e: clean_label(e[0].stem, labels).lower())


def base_element(kind, x, y, width, height, group_id, now):
    return {
        "id": rand_id(),
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
        "seed": rand_int(),
        "version": 1,
        "versionNonce": rand_int(),
        "isDeleted": False,
        "boundElements": None,
        "updated": now,
        "link": None,
        "locked": False,
    }


def build_elements(file_id, label, now, ox=0, oy=0):
    group_id = rand_id()

    image = base_element("image", ox, oy, ICON_SIZE, ICON_SIZE, group_id, now)
    image.update({"status": "saved", "fileId": file_id, "scale": [1, 1], "crop": None})

    text = wrap_label(label)
    lines = text.split("\n")
    width = round(max(len(line) for line in lines) * CHAR_WIDTH, 2)
    height = round(len(lines) * FONT_SIZE * LINE_HEIGHT, 2)
    label_el = base_element(
        "text", ox + ICON_SIZE / 2 - width / 2, oy + LABEL_Y, width, height, group_id, now
    )
    label_el.update({
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
    })
    return [image, label_el]


def build_pack(name, pack, now):
    labels = pack.get("labels", {})
    stored = ICONS / name
    downloads = sorted(DOWNLOADS.glob(pack["download"]), key=lambda p: p.stat().st_mtime)
    source = downloads[-1] if downloads else stored
    if not source.exists():
        print(f"[{name}] skipped: no downloads/{pack['download']} and no icons/{name}/")
        return
    icons = collect_icons(source, labels)

    if source != stored:
        shutil.rmtree(stored, ignore_errors=True)
        for path, svg in icons:
            target = stored / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(svg)

    items, files, scene_elements = [], {}, []
    for i, (path, svg) in enumerate(icons):
        file_id = uuid.uuid5(FILE_ID_NAMESPACE, base64.b64encode(svg).decode()).hex
        files[file_id] = {
            "mimeType": "image/svg+xml",
            "id": file_id,
            "dataURL": "data:image/svg+xml;base64," + base64.b64encode(svg).decode("ascii"),
            "created": now,
            "lastRetrieved": now,
        }
        label = clean_label(path.stem, labels)
        items.append({
            "id": rand_id(),
            "status": "unpublished",
            "elements": build_elements(file_id, label, now),
            "created": now,
            "name": label,
        })
        col, row = i % SCENE_COLUMNS, i // SCENE_COLUMNS
        scene_elements += build_elements(file_id, label, now, col * SCENE_CELL_W, row * SCENE_CELL_H)

    library = {
        "type": "excalidrawlib",
        "version": 2,
        "source": SOURCE,
        "libraryItems": items,
        "files": files,  # ignored by excalidraw.com; see module docstring
    }
    scene = {
        "type": "excalidraw",
        "version": 2,
        "source": SOURCE,
        "elements": scene_elements,
        "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None},
        "files": files,
    }

    LIBRARIES.mkdir(exist_ok=True)
    lib_path = LIBRARIES / f"{name}-miro-style.excalidrawlib"
    scene_path = LIBRARIES / f"{name}-miro-style.excalidraw"
    lib_path.write_text(json.dumps(library, indent=2), encoding="utf-8")
    scene_path.write_text(json.dumps(scene), encoding="utf-8")
    print(f"[{name}] packaged {len(items)} icons from {source.relative_to(ROOT)} -> {lib_path.relative_to(ROOT)}")


def main():
    now = int(time.time() * 1000)
    for name, pack in PACKS.items():
        build_pack(name, pack, now)


if __name__ == "__main__":
    main()
