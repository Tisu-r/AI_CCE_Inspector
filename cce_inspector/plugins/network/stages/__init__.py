"""
Network-specific 3-stage CCE analysis pipeline.

Stage 1: Asset Identification - Identify device vendor, OS, type, role
Stage 2: Criteria Mapping - Map applicable CCE checks to device
Stage 3: Vulnerability Assessment - Evaluate compliance directly from original config
"""

from .stage1_asset import AssetIdentificationStage, AssetInfo, identify_asset
from .stage2_criteria import CriteriaMappingStage, CriteriaMappingResult, CheckMapping, map_criteria
from .stage4_assessment import (
    VulnerabilityAssessmentStage,
    VulnerabilityAssessmentResult,
    AssessmentResult,
    assess_vulnerabilities
)

__all__ = [
    # Stage 1
    "AssetIdentificationStage",
    "AssetInfo",
    "identify_asset",
    # Stage 2
    "CriteriaMappingStage",
    "CriteriaMappingResult",
    "CheckMapping",
    "map_criteria",
    # Stage 3
    "VulnerabilityAssessmentStage",
    "VulnerabilityAssessmentResult",
    "AssessmentResult",
    "assess_vulnerabilities"
]
