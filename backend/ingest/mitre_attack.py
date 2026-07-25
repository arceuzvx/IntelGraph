"""
IntelGraph — MITRE ATT&CK ingestion CLI.

Orchestrates the full pipeline:
    1. Download / cache the Enterprise ATT&CK STIX dataset
    2. Parse attack-pattern objects
    3. Generate embeddings and bulk-insert into VectorAI
    4. Save filter metadata for the API

Usage:
    cd backend
    python -m ingest.mitre_attack            # use cached dataset
    python -m ingest.mitre_attack --refresh   # force re-download
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Optional

from actian_vectorai import VectorAIClient

from ingest.downloader import download_attack_dataset
from ingest.parser import parse_attack_techniques
from ingest.bulk_insert import bulk_insert_techniques

# Metadata output path
_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
FILTERS_PATH = _DATA_DIR / "filters.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def _save_filter_metadata(techniques) -> None:
    """Extract unique platforms and tactics and write to filters.json."""
    platforms: set = set()
    tactics: set = set()
    for t in techniques:
        platforms.update(t.platforms)
        tactics.update(t.tactics)

    metadata = {
        "platforms": sorted(platforms),
        "tactics": sorted(tactics),
    }
    FILTERS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(FILTERS_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    log.info("Saved filter metadata to %s", FILTERS_PATH)


def ingest_attack_data(
    *, refresh: bool = False, client: Optional[VectorAIClient] = None
) -> int:
    """Download (or load) and ingest the MITRE ATT&CK dataset once.

    Returns the number of vectors written. The API invokes this only for an
    empty collection; the CLI remains available for explicit refreshes.
    """
    # Step 1: Download / load
    log.info("=" * 60)
    log.info("MITRE ATT&CK Ingestion Pipeline")
    log.info("=" * 60)
    stix_bundle = download_attack_dataset(refresh=refresh)

    # Step 2: Parse
    techniques = parse_attack_techniques(stix_bundle)
    log.info("Parsed %d techniques.", len(techniques))

    if not techniques:
        log.error("No techniques found. Aborting.")
        raise RuntimeError("No MITRE ATT&CK techniques found; ingestion aborted.")

    # Step 3: Save filter metadata
    _save_filter_metadata(techniques)

    # Step 4: Bulk embed + insert
    inserted = bulk_insert_techniques(techniques, client=client)
    log.info("=" * 60)
    log.info("Ingestion complete. %d techniques inserted.", inserted)
    log.info("=" * 60)
    return inserted


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest MITRE ATT&CK into IntelGraph")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Force re-download of the ATT&CK dataset",
    )
    args = parser.parse_args()
    ingest_attack_data(refresh=args.refresh)


if __name__ == "__main__":
    main()
