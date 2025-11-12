"""
Stage 3: Configuration Parsing

Extracts security configuration values from device configuration
based on applicable CCE checks.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from cce_inspector.core.ai_clients.base import BaseAIClient, AIResponse
from cce_inspector.core.validators import ResponseValidator, ValidationError, Stage
from cce_inspector.core.utils import FileHandler, JSONParser, get_logger

from .stage1_asset import AssetInfo
from .stage2_criteria import CriteriaMappingResult


@dataclass
class ParsedCheckConfig:
    """
    Parsed configuration for a single check.

    Attributes:
        check_id: CCE check identifier
        found_config: List of configuration lines found
        extracted_values: Dictionary of extracted configuration values
        config_present: Whether relevant configuration was found
    """
    check_id: str
    found_config: List[str] = field(default_factory=list)
    extracted_values: Dict[str, Any] = field(default_factory=dict)
    config_present: bool = False

    @classmethod
    def from_dict(cls, check_id: str, data: Dict[str, Any]) -> 'ParsedCheckConfig':
        """Create ParsedCheckConfig from dictionary."""
        return cls(
            check_id=check_id,
            found_config=data.get('found_config', []),
            extracted_values=data.get('extracted_values', {}),
            config_present=data.get('config_present', False)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'found_config': self.found_config,
            'extracted_values': self.extracted_values,
            'config_present': self.config_present
        }


@dataclass
class ConfigParsingResult:
    """
    Configuration parsing result.

    Attributes:
        parsed_config: Dictionary mapping check_id to parsed configuration
    """
    parsed_config: Dict[str, ParsedCheckConfig] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConfigParsingResult':
        """Create ConfigParsingResult from dictionary."""
        parsed_config = {}
        for check_id, check_data in data.get('parsed_config', {}).items():
            parsed_config[check_id] = ParsedCheckConfig.from_dict(check_id, check_data)

        return cls(parsed_config=parsed_config)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'parsed_config': {
                check_id: config.to_dict()
                for check_id, config in self.parsed_config.items()
            }
        }

    def get_check_config(self, check_id: str) -> Optional[ParsedCheckConfig]:
        """Get parsed configuration for a specific check."""
        return self.parsed_config.get(check_id)


class ConfigParsingStage:
    """
    Stage 3: Parse configuration to extract security values.
    """

    def __init__(
        self,
        ai_client: BaseAIClient,
        baseline_file: str = "cce_baseline.json",
        templates_dir: Optional[Path] = None
    ):
        """
        Initialize Stage 3.

        Args:
            ai_client: AI client instance for analysis
            baseline_file: CCE baseline filename
            templates_dir: Optional custom templates directory
        """
        self.ai_client = ai_client
        self.baseline_file = baseline_file
        self.templates_dir = templates_dir
        self.logger = get_logger()

    def _load_prompt_template(self) -> str:
        """
        Load Stage 3 prompt template.

        Returns:
            str: Prompt template content
        """
        try:
            return FileHandler.load_prompt_template(
                "stage3_config_parsing",
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

    def _filter_applicable_checks(
        self,
        cce_baseline: List[Dict[str, Any]],
        applicable_check_ids: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Filter CCE baseline to only include applicable checks.

        Args:
            cce_baseline: Full CCE baseline
            applicable_check_ids: List of applicable check IDs

        Returns:
            Filtered list of CCE check definitions
        """
        return [
            check for check in cce_baseline
            if check['check_id'] in applicable_check_ids
        ]

    def _build_prompt(
        self,
        config: str,
        asset_info: AssetInfo,
        applicable_checks: List[Dict[str, Any]]
    ) -> str:
        """
        Build prompt for configuration parsing.

        Args:
            config: Device configuration text
            asset_info: Asset identification information
            applicable_checks: List of applicable CCE checks

        Returns:
            str: Complete prompt
        """
        template = self._load_prompt_template()

        # Format asset information
        asset_json = JSONParser.pretty_print(asset_info.to_dict())

        # Format applicable checks (include only relevant fields)
        checks_summary = []
        for check in applicable_checks:
            checks_summary.append({
                "check_id": check["check_id"],
                "title": check["title"],
                "check_patterns": check.get("check_patterns", {}),
                "vendor_commands": check.get("vendor_commands", {}).get(asset_info.vendor.lower(), {})
            })
        checks_json = JSONParser.pretty_print(checks_summary)

        # Replace placeholders
        prompt = template.replace("{{CONFIGURATION}}", config)
        prompt = prompt.replace("{{ASSET_INFO}}", asset_json)
        prompt = prompt.replace("{{APPLICABLE_CHECKS}}", checks_json)

        return prompt

    def parse_config(
        self,
        config: str,
        asset_info: AssetInfo,
        criteria_result: CriteriaMappingResult
    ) -> ConfigParsingResult:
        """
        Parse configuration to extract security values.

        Args:
            config: Device configuration text
            asset_info: Asset identification information
            criteria_result: Criteria mapping result from Stage 2

        Returns:
            ConfigParsingResult: Parsed configuration values

        Raises:
            ValidationError: If AI response validation fails
            Exception: If AI request fails
        """
        self.logger.stage_start("Configuration Parsing", 3)

        try:
            # Load CCE baseline
            self.logger.info("Loading CCE baseline...")
            cce_baseline = self._load_cce_baseline()

            # Filter to only applicable checks
            applicable_check_ids = criteria_result.get_applicable_check_ids()
            applicable_checks = self._filter_applicable_checks(
                cce_baseline,
                applicable_check_ids
            )

            self.logger.info(f"Parsing {len(applicable_checks)} applicable checks")

            # Build prompt
            prompt = self._build_prompt(config, asset_info, applicable_checks)

            # Get AI response
            self.logger.info("Analyzing configuration to extract security values...")
            response: AIResponse = self.ai_client.generate(
                prompt=prompt,
                system_prompt="You are a network configuration parsing expert."
            )

            self.logger.debug(f"AI response received ({response.tokens_used.get('total', 0)} tokens)")

            # Validate and parse response
            self.logger.info("Validating configuration parsing response...")
            validated_data = ResponseValidator.validate_stage(
                Stage.CONFIG_PARSING,
                response.content
            )

            # Convert to result object
            result = ConfigParsingResult.from_dict(validated_data)

            # Count how many configs were found
            configs_found = sum(
                1 for config in result.parsed_config.values()
                if config.config_present
            )

            self.logger.info(
                f"✓ Configuration parsed: {configs_found}/{len(applicable_checks)} "
                f"checks have relevant configuration"
            )

            return result

        except ValidationError as e:
            self.logger.error(f"Response validation failed: {str(e)}")
            self.logger.debug(f"Raw response: {response.content[:500]}...")
            raise
        except Exception as e:
            self.logger.error(f"Configuration parsing failed: {str(e)}")
            raise


def parse_config(
    config: str,
    asset_info: AssetInfo,
    criteria_result: CriteriaMappingResult,
    ai_client: BaseAIClient,
    templates_dir: Optional[Path] = None
) -> ConfigParsingResult:
    """
    Convenience function to parse configuration.

    Args:
        config: Device configuration text
        asset_info: Asset identification information
        criteria_result: Criteria mapping result
        ai_client: AI client instance
        templates_dir: Optional custom templates directory

    Returns:
        ConfigParsingResult: Parsing result
    """
    stage = ConfigParsingStage(ai_client, templates_dir=templates_dir)
    return stage.parse_config(config, asset_info, criteria_result)
