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
import sys
from pathlib import Path

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


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest MITRE ATT&CK into IntelGraph")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Force re-download of the ATT&CK dataset",
    )
    args = parser.parse_args()

    # Step 1: Download / load
    log.info("=" * 60)
    log.info("MITRE ATT&CK Ingestion Pipeline")
    log.info("=" * 60)
    stix_bundle = download_attack_dataset(refresh=args.refresh)

    # Step 2: Parse
    techniques = parse_attack_techniques(stix_bundle)
    log.info("Parsed %d techniques.", len(techniques))

    if not techniques:
        log.error("No techniques found. Aborting.")
        sys.exit(1)

    # Step 3: Save filter metadata
    _save_filter_metadata(techniques)

    # Step 4: Bulk embed + insert
    inserted = bulk_insert_techniques(techniques)
    log.info("=" * 60)
    log.info("Ingestion complete. %d techniques inserted.", inserted)
    log.info("=" * 60)


if __name__ == "__main__":
    main()
