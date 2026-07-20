"""
IntelGraph — MITRE ATT&CK STIX parser.

Parses the Enterprise ATT&CK STIX bundle and extracts technique objects,
filtering out revoked and deprecated entries.
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class MitreTechnique:
    """Strongly-typed representation of a single ATT&CK technique."""

    technique_id: str
    name: str
    description: str
    platforms: List[str]
    tactics: List[str]
    data_sources: List[str]
    detection: str
    url: str
    external_references: List[Dict[str, str]]
    point_id: int  # deterministic integer ID for VectorAI


def _technique_id_to_point_id(technique_id: str) -> int:
    """Convert a technique ID to a deterministic integer for VectorAI.

    T1555     → 1555000
    T1555.001 → 1555001
    """
    raw = technique_id.lstrip("T")
    parts = raw.split(".")
    base = int(parts[0]) * 1000
    if len(parts) > 1:
        base += int(parts[1])
    return base


def _clean_description(text: str) -> str:
    """Strip STIX citation markers like (Citation: ...) from description text."""
    return re.sub(r"\(Citation:[^)]*\)", "", text).strip()


def _extract_technique_id(obj: Dict[str, Any]) -> Optional[str]:
    """Extract the Txxxx ID from external_references."""
    for ref in obj.get("external_references", []):
        ext_id = ref.get("external_id", "")
        if ext_id.startswith("T"):
            return ext_id
    return None


def _extract_url(obj: Dict[str, Any]) -> str:
    """Extract the MITRE ATT&CK URL from external_references."""
    for ref in obj.get("external_references", []):
        if ref.get("source_name") == "mitre-attack":
            return ref.get("url", "")
    return ""


def _extract_tactics(obj: Dict[str, Any]) -> List[str]:
    """Extract kill-chain phase names (tactics)."""
    phases = obj.get("kill_chain_phases", [])
    return [
        p["phase_name"].replace("-", " ").title()
        for p in phases
        if p.get("kill_chain_name") == "mitre-attack"
    ]


def _extract_references(obj: Dict[str, Any]) -> List[Dict[str, str]]:
    """Extract external references as simple dicts."""
    refs: List[Dict[str, str]] = []
    for ref in obj.get("external_references", []):
        entry: Dict[str, str] = {}
        if "source_name" in ref:
            entry["source"] = ref["source_name"]
        if "url" in ref:
            entry["url"] = ref["url"]
        if "external_id" in ref:
            entry["id"] = ref["external_id"]
        if entry:
            refs.append(entry)
    return refs


def parse_attack_techniques(stix_bundle: Dict[str, Any]) -> List[MitreTechnique]:
    """Parse the STIX bundle and return a list of MitreTechnique objects.

    Filters out:
        - Objects that are not attack-patterns
        - Revoked techniques
        - Deprecated techniques

    Args:
        stix_bundle: The parsed enterprise-attack.json STIX bundle.

    Returns:
        A sorted list of MitreTechnique objects.
    """
    techniques: List[MitreTechnique] = []

    for obj in stix_bundle.get("objects", []):
        # Only process attack-pattern objects
        if obj.get("type") != "attack-pattern":
            continue

        # Skip revoked
        if obj.get("revoked", False):
            continue

        # Skip deprecated
        if obj.get("x_mitre_deprecated", False):
            continue

        technique_id = _extract_technique_id(obj)
        if not technique_id:
            continue

        raw_desc = obj.get("description", "")
        description = _clean_description(raw_desc)

        technique = MitreTechnique(
            technique_id=technique_id,
            name=obj.get("name", ""),
            description=description,
            platforms=obj.get("x_mitre_platforms", []),
            tactics=_extract_tactics(obj),
            data_sources=obj.get("x_mitre_data_sources", []),
            detection=_clean_description(obj.get("x_mitre_detection", "")),
            url=_extract_url(obj),
            external_references=_extract_references(obj),
            point_id=_technique_id_to_point_id(technique_id),
        )
        techniques.append(technique)

    # Sort by technique ID for deterministic ordering
    techniques.sort(key=lambda t: t.technique_id)
    log.info("Parsed %d active techniques (revoked/deprecated excluded).", len(techniques))
    return techniques
