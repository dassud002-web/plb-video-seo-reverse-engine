#!/usr/bin/env python3
"""
Evidence Data Structures and Tagging for PLB Story Forge
=========================================================
Strict separation of:
- SOURCE_EVIDENCE (Fact directly observed in forensic/video data)
- INFERENCE (High-confidence deduction from observed facts)
- CREATIVE_EXPANSION (Narrative extension derived from Story DNA)
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from enum import Enum

class EvidenceLevel(str, Enum):
    SOURCE_EVIDENCE = "SOURCE_EVIDENCE"
    INFERENCE = "INFERENCE"
    CREATIVE_EXPANSION = "CREATIVE_EXPANSION"

class EvidenceType(str, Enum):
    VISUAL_KEYFRAME = "visual_keyframe"
    AUDIO_ANALYSIS = "audio_analysis"
    CONTAINER_METADATA = "container_metadata"
    OCR_SCAN = "ocr_scan"
    C2PA_PROVENANCE = "c2pa_provenance"
    SIDECAR_DOC = "sidecar_doc"
    DERIVED_DNA = "derived_dna"

@dataclass
class EvidenceItem:
    evidence_id: str
    level: str  # SOURCE_EVIDENCE, INFERENCE, CREATIVE_EXPANSION
    evidence_type: str
    timestamp_or_frame: str
    fact: str
    inference: Optional[str] = None
    confidence: str = "100% (Fact)"
    source_reference: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvidenceItem":
        return cls(**data)
