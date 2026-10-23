import json
from datetime import UTC, datetime

from inf8239_u03.config import MOVIELENS_URL, ROOT
from inf8239_u03.data import download_zip

destination, digest = download_zip(MOVIELENS_URL, ROOT / "data/raw")
(ROOT / "reports").mkdir(exist_ok=True)
(ROOT / "reports/download_manifest.json").write_text(
    json.dumps(
        {
            "url": MOVIELENS_URL,
            "downloaded_utc": datetime.now(UTC).isoformat(),
            "sha256_zip": digest,
            "source": "GroupLens Research, University of Minnesota",
            "license_url": "https://files.grouplens.org/datasets/movielens/ml-latest-small-README.html",
        },
        indent=2,
    ),
    encoding="utf-8",
)
print("Destino:", destination)
print("SHA-256:", digest)
