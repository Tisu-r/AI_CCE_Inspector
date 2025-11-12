"""
Stage 2: Criteria Mapping

Maps applicable CCE checks based on asset information and device profile.
Filters out checks that are not relevant to the identified device type.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from cce_inspector.core.ai_clients.base import BaseAIClient, AIResponse
from cce_inspector.core.validators import ResponseValidator, ValidationError, Stage
from cce_inspector.core.utils import FileHandler, JSONParser, get_logger

from .stage1_asset import AssetInfo


@dataclass
class CheckMapping:
    """
    Individual check mapping result.

    Attributes:
        check_id: CCE check identifier (e.g., 'N-01')
        reason: Reason for inclusion/exclusion
    """
    check_id: str
    reason: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CheckMapping':
        """Create CheckMapping from dictionary."""
        return cls(
            check_id=data['check_id'],
            reason=data['reason']
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'check_id': self.check_id,
            'reason': self.reason
        }


@dataclass
class CriteriaMappingResult:
    """
    Criteria mapping result.

    Attributes:
        applicable_checks: List of checks applicable to this asset
        excluded_checks: List of checks not applicable to this asset
    """
    applicable_checks: List[CheckMapping]
    excluded_checks: List[CheckMapping]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CriteriaMappingResult':
        """Create CriteriaMappingResult from dictionary."""
        return cls(
            applicable_checks=[
                CheckMapping.from_dict(check)
                for check in data['applicable_checks']
            ],
            excluded_checks=[
                CheckMapping.from_dict(check)
                for check in data['excluded_checks']
            ]
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'applicable_checks': [check.to_dict() for check in self.applicable_checks],
            'excluded_checks': [check.to_dict() for check in self.excluded_checks]
        }

    def get_applicable_check_ids(self) -> List[str]:
        """Get list of applicable check IDs."""
        return [check.check_id for check in self.applicable_checks]


class CriteriaMappingStage:
    """
    Stage 2: Map applicable CCE criteria to asset.
    """

    def __init__(
        self,
        ai_client: BaseAIClient,
        baseline_file: str = "cce_baseline.json",
        profiles_file: str = "device_profiles.json",
        templates_dir: Optional[Path] = None
    ):
        """
        Initialize Stage 2.

        Args:
            ai_client: AI client instance for analysis
            baseline_file: CCE baseline filename
            profiles_file: Device profiles filename
            templates_dir: Optional custom templates directory
        """
        self.ai_client = ai_client
        self.baseline_file = baseline_file
        self.profiles_file = profiles_file
        self.templates_dir = templates_dir
        self.logger = get_logger()

    def _load_prompt_template(self) -> str:
        """
        Load Stage 2 prompt template.

        Returns:
            str: Prompt template content
        """
        try:
            return FileHandler.load_prompt_template(
                "stage2_criteria_mapping",
                self.templates_dir
            )
        except FileNotFoundError as e:
            self.logger.error(f"Failed to load prompt template: {str(e)}")
            raise

    def _load_cce_baseline(self) -> List[Dict[str, Any]]:
        """
        Load CCE baseline for network devices.

        Returns:
            List of CCE check definitions
        """
        try:
            return FileHandler.load_cce_baseline("network", self.baseline_file)
        except FileNotFoundError as e:
            self.logger.error(f"Failed to load CCE baseline: {str(e)}")
            raise

    def _load_device_profile(self, asset_info: AssetInfo) -> Optional[Dict[str, Any]]:
        """
        Load device profile matching the asset.

        Args:
            asset_info: Asset identification information

        Returns:
            Device profile dict or None if not found
        """
        try:
            profiles = FileHandler.load_device_profiles("network", self.profiles_file)

            # Try to match by vendor and OS type
            profile_key = f"{asset_info.vendor}_{asset_info.os_type}".lower()

            if profile_key in profiles:
                return profiles[profile_key]

            # Fallback to vendor only
            vendor_key = asset_info.vendor.lower()
            for key, profile in profiles.items():
                if key.startswith(vendor_key):
                    self.logger.warning(
                        f"Exact profile not found, using fallback: {key}"
                    )
                    return profile

            self.logger.warning(f"No device profile found for {profile_key}")
            return None

        except FileNotFoundError as e:
            self.logger.error(f"Failed to load device profiles: {str(e)}")
            return None

    def _build_prompt(
        self,
        asset_info: AssetInfo,
        cce_baseline: List[Dict[str, Any]],
        device_profile: Optional[Dict[str, Any]]
    ) -> str:
        """
        Build prompt for criteria mapping.

        Args:
            asset_info: Asset identification information
            cce_baseline: CCE baseline checks
            device_profile: Device profile information

        Returns:
            str: Complete prompt
        """
        template = self._load_prompt_template()

        # Format asset information
        asset_json = JSONParser.pretty_print(asset_info.to_dict())

        # Format CCE baseline (simplified for prompt)
        baseline_summary = []
        for check in cce_baseline:
            baseline_summary.append({
                "check_id": check["check_id"],
                "title": check["title"],
                "severity": check["severity"],
                "description": check.get("description", "")
            })
        baseline_json = JSONParser.pretty_print(baseline_summary)

        # Format device profile
        profile_json = JSONParser.pretty_print(device_profile) if device_profile else "{}"

        # Replace placeholders
        prompt = template.replace("{{ASSET_INFO}}", asset_json)
        prompt = prompt.replace("{{CCE_BASELINE}}", baseline_json)
        prompt = prompt.replace("{{DEVICE_PROFILE}}", profile_json)

        return prompt

    def map_criteria(
        self,
        asset_info: AssetInfo,
        config: Optional[str] = None
    ) -> CriteriaMappingResult:
        """
        Map applicable CCE criteria to the identified asset.

        Args:
            asset_info: Asset identification information
            config: Optional configuration text for additional context

        Returns:
            CriteriaMappingResult: Mapping of applicable/excluded checks

        Raises:
            ValidationError: If AI response validation fails
            Exception: If AI request fails
        """
        self.logger.stage_start("Criteria Mapping", 2)

        try:
            # Load CCE baseline and device profile
            self.logger.info("Loading CCE baseline and device profile...")
            cce_baseline = self._load_cce_baseline()
            device_profile = self._load_device_profile(asset_info)

            self.logger.info(f"Loaded {len(cce_baseline)} CCE checks from baseline")

            # Build prompt
            prompt = self._build_prompt(asset_info, cce_baseline, device_profile)

            # Get AI response
            self.logger.info("Analyzing applicable CCE criteria...")
            response: AIResponse = self.ai_client.generate(
                prompt=prompt,
                system_prompt="You are a network security expert mapping compliance criteria to devices."
            )

            self.logger.debug(f"AI response received ({response.tokens_used.get('total', 0)} tokens)")

            # Validate and parse response
            self.logger.info("Validating criteria mapping response...")
            validated_data = ResponseValidator.validate_stage(
                Stage.CRITERIA_MAPPING,
                response.content
            )

            # Convert to result object
            result = CriteriaMappingResult.from_dict(validated_data)

            self.logger.info(
                f"✓ Criteria mapped: {len(result.applicable_checks)} applicable, "
                f"{len(result.excluded_checks)} excluded"
            )

            return result

        except ValidationError as e:
            self.logger.error(f"Response validation failed: {str(e)}")
            self.logger.debug(f"Raw response: {response.content[:500]}...")
            raise
        except Exception as e:
            self.logger.error(f"Criteria mapping failed: {str(e)}")
            raise


def map_criteria(
    asset_info: AssetInfo,
    ai_client: BaseAIClient,
    config: Optional[str] = None,
    templates_dir: Optional[Path] = None
) -> CriteriaMappingResult:
    """
    Convenience function to map criteria for an asset.

    Args:
        asset_info: Asset identification information
        ai_client: AI client instance
        config: Optional configuration text
        templates_dir: Optional custom templates directory

    Returns:
        CriteriaMappingResult: Mapping result
    """
    stage = CriteriaMappingStage(ai_client, templates_dir=templates_dir)
    return stage.map_criteria(asset_info, config)
