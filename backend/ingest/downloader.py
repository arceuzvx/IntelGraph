"""
IntelGraph — MITRE ATT&CK STIX dataset downloader.

Downloads the Enterprise ATT&CK STIX bundle from the official
MITRE CTI GitHub repository and caches it locally.

Source:
    https://github.com/mitre/cti
"""

import json
import logging
import urllib.request
from pathlib import Path
from typing import Any, Dict

log = logging.getLogger(__name__)

ATTACK_URL: str = (
    "https://raw.githubusercontent.com/mitre/cti/"
    "master/enterprise-attack/enterprise-attack.json"
)

# Default cache location: IntelGraph/data/enterprise-attack.json
_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DEFAULT_CACHE_PATH: Path = _DATA_DIR / "enterprise-attack.json"


def download_attack_dataset(
    cache_path: Path = DEFAULT_CACHE_PATH,
    refresh: bool = False,
) -> Dict[str, Any]:
    """Download the ATT&CK STIX bundle or load it from cache.

    Args:
        cache_path: Where to store/read the cached JSON file.
        refresh:    If True, re-download even if the cache exists.

    Returns:
        The parsed STIX bundle as a Python dict.
    """
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    if cache_path.exists() and not refresh:
        log.info("Loading cached dataset from %s", cache_path)
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)

    log.info("Downloading ATT&CK dataset from %s ...", ATTACK_URL)
    req = urllib.request.Request(ATTACK_URL, headers={"User-Agent": "IntelGraph/0.1"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        raw = resp.read()

    data: Dict[str, Any] = json.loads(raw)

    with open(cache_path, "wb") as f:
        f.write(raw)
    log.info("Saved dataset to %s (%.1f MB)", cache_path, len(raw) / 1_048_576)

    return data
