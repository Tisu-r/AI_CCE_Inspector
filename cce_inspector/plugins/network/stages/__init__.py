"""
Network-specific 4-stage CCE analysis pipeline.

Stage 1: Asset Identification - Identify device vendor, OS, type, role
Stage 2: Criteria Mapping - Map applicable CCE checks to device
Stage 3: Configuration Parsing - Extract security configuration values
Stage 4: Vulnerability Assessment - Evaluate compliance and vulnerabilities
"""

from .stage1_asset import AssetIdentificationStage, AssetInfo, identify_asset
from .stage2_criteria import CriteriaMappingStage, CriteriaMappingResult, CheckMapping, map_criteria
from .stage3_parsing import ConfigParsingStage, ConfigParsingResult, ParsedCheckConfig, parse_config
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
    "ConfigParsingStage",
    "ConfigParsingResult",
    "ParsedCheckConfig",
    "parse_config",
    # Stage 4
    "VulnerabilityAssessmentStage",
    "VulnerabilityAssessmentResult",
    "AssessmentResult",
    "assess_vulnerabilities"
]
