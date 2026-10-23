"""Download pinned upstream IDX files and preserve provenance."""

import gzip
import hashlib
import json
import struct
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import requests

ROOT = Path(__file__).resolve().parents[2]
CLASSES = [
    "T-shirt/top",
    "Trouser",
    "Pullover",
    "Dress",
    "Coat",
    "Sandal",
    "Shirt",
    "Sneaker",
    "Bag",
    "Ankle boot",
]
FILES = [
    "train-images-idx3-ubyte.gz",
    "train-labels-idx1-ubyte.gz",
    "t10k-images-idx3-ubyte.gz",
    "t10k-labels-idx1-ubyte.gz",
]


def parse_idx(content):
    if len(content) < 8:
        raise ValueError("IDX header truncated")
    magic = struct.unpack(">I", content[:4])[0]
    if magic == 2051:
        if len(content) < 16:
            raise ValueError("IDX image header truncated")
        _, count, rows, cols = struct.unpack(">IIII", content[:16])
        if (rows, cols) != (28, 28) or len(content) != 16 + count * rows * cols:
            raise ValueError("IDX image shape or byte count invalid")
        return (
            np.frombuffer(content[16:], dtype=np.uint8).reshape(count, 28, 28, 1).copy()
        )
    if magic == 2049:
        count = struct.unpack(">I", content[4:8])[0]
        if len(content) != 8 + count:
            raise ValueError("IDX label byte count invalid")
        labels = np.frombuffer(content[8:], dtype=np.uint8).copy()
        if not np.isin(labels, range(10)).all():
            raise ValueError("Unknown class")
        return labels
    raise ValueError("Invalid IDX magic")


def load_data():
    directory = ROOT / "data/raw"
    directory.mkdir(parents=True, exist_ok=True)
    manifest_path = ROOT / "reports/download_manifest.json"
    manifest_path.parent.mkdir(exist_ok=True)
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        commit = manifest["upstream_commit"]
    else:
        response = requests.get(
            "https://api.github.com/repos/zalandoresearch/fashion-mnist/commits/master",
            timeout=60,
        )
        response.raise_for_status()
        commit = response.json()["sha"]
        manifest = {
            "source": "Zalando Research / Fashion-MNIST",
            "upstream_commit": commit,
            "license": "MIT",
            "license_url": f"https://github.com/zalandoresearch/fashion-mnist/blob/{commit}/LICENSE",
            "files": {},
        }
    arrays = []
    for name in FILES:
        path = directory / name
        url = f"https://raw.githubusercontent.com/zalandoresearch/fashion-mnist/{commit}/data/fashion/{name}"
        if not path.exists():
            response = requests.get(url, timeout=120)
            response.raise_for_status()
            path.write_bytes(response.content)
        content = path.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        old = manifest["files"].get(name)
        if old and old["sha256"] != digest:
            raise ValueError(f"Dataset hash mismatch: {name}")
        manifest["files"][name] = old or {
            "url": url,
            "sha256": digest,
            "bytes": len(content),
            "downloaded_utc": datetime.now(UTC).isoformat(),
        }
        arrays.append(parse_idx(gzip.decompress(content)))
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    if [len(a) for a in arrays] != [60000, 60000, 10000, 10000]:
        raise ValueError("Unexpected Fashion-MNIST sizes")
    return arrays


def split_training(images, labels, seed=42, limit=None):
    from sklearn.model_selection import train_test_split

    indices = np.arange(len(images))
    fit_idx, val_idx = train_test_split(
        indices, test_size=10000, random_state=seed, stratify=labels
    )
    if limit is not None:
        if limit < 100:
            raise ValueError("limit must be >=100")
        # Uniform seeded subset of fit only; validation/test are unchanged.
        fit_idx = np.random.default_rng(seed).choice(
            fit_idx, min(limit, len(fit_idx)), replace=False
        )
    return fit_idx, val_idx


def normalize(images):
    if images.dtype != np.uint8 or images.shape[1:] != (28, 28, 1):
        raise ValueError("Expected uint8 NHWC 28x28x1")
    return images.astype(np.float32) / 255.0
