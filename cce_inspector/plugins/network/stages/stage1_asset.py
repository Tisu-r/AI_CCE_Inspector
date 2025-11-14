"""
Stage 1: Asset Identification

Analyzes network device configuration to identify vendor, OS type, version,
hostname, device type, and role.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

from cce_inspector.core.ai_clients.base import BaseAIClient, AIResponse
from cce_inspector.core.validators import ResponseValidator, ValidationError, Stage
from cce_inspector.core.utils import FileHandler, JSONParser, get_logger


@dataclass
class AssetInfo:
    """
    Asset identification result.

    Attributes:
        vendor: Device vendor (e.g., 'cisco', 'juniper')
        os_type: Operating system type (e.g., 'ios', 'junos')
        os_version: OS version string
        hostname: Device hostname
        device_type: Type of device (e.g., 'router', 'switch', 'firewall')
        device_role: Device role (e.g., 'core', 'edge', 'access')
        confidence: Confidence score (0.0 to 1.0) or string ('high', 'medium', 'low')
    """
    vendor: str
    os_type: str
    os_version: str
    hostname: str
    device_type: str
    device_role: str
    confidence: float | str  # Can be numeric (0-1) or string ('high'/'medium'/'low')

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AssetInfo':
        """Create AssetInfo from dictionary."""
        return cls(
            vendor=data['vendor'],
            os_type=data['os_type'],
            os_version=data['os_version'],
            hostname=data['hostname'],
            device_type=data['device_type'],
            device_role=data['device_role'],
            confidence=data['confidence']
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'vendor': self.vendor,
            'os_type': self.os_type,
            'os_version': self.os_version,
            'hostname': self.hostname,
            'device_type': self.device_type,
            'device_role': self.device_role,
            'confidence': self.confidence
        }


class AssetIdentificationStage:
    """
    Stage 1: Identify asset information from configuration.
    """

    def __init__(
        self,
        ai_client: BaseAIClient,
        templates_dir: Optional[Path] = None
    ):
        """
        Initialize Stage 1.

        Args:
            ai_client: AI client instance for analysis
            templates_dir: Optional custom templates directory
        """
        self.ai_client = ai_client
        self.templates_dir = templates_dir
        self.logger = get_logger()

    def _load_prompt_template(self) -> str:
        """
        Load Stage 1 prompt template.

        Returns:
            str: Prompt template content
        """
        try:
            return FileHandler.load_prompt_template(
                "stage1_asset_identification",
                self.templates_dir
            )
        except FileNotFoundError as e:
            self.logger.error(f"Failed to load prompt template: {str(e)}")
            raise

    def _build_prompt(self, config: str) -> str:
        """
        Build prompt for asset identification.

        Args:
            config: Device configuration text

        Returns:
            str: Complete prompt with configuration embedded
        """
        template = self._load_prompt_template()

        # Replace placeholder with actual configuration
        prompt = template.replace("{{CONFIGURATION}}", config)

        return prompt

    def analyze(self, config: str) -> AssetInfo:
        """
        Analyze configuration to identify asset information.

        Args:
            config: Device configuration text (e.g., show running-config output)

        Returns:
            AssetInfo: Identified asset information

        Raises:
            ValidationError: If AI response validation fails
            Exception: If AI request fails
        """
        self.logger.stage_start("Asset Identification", 1)

        try:
            # Build prompt with configuration
            prompt = self._build_prompt(config)

            # Get AI response
            self.logger.info("Sending configuration to AI for asset identification...")
            response: AIResponse = self.ai_client.generate(
                prompt=prompt,
                system_prompt="You are a network security expert analyzing device configurations."
            )

            self.logger.debug(f"AI response received ({response.tokens_used.get('total', 0)} tokens)")

            # Validate and parse response
            self.logger.info("Validating AI response format...")
            validated_data = ResponseValidator.validate_stage(
                Stage.ASSET_IDENTIFICATION,
                response.content
            )

            # Convert to AssetInfo object
            asset_info = AssetInfo.from_dict(validated_data)

            # Format confidence for display
            if isinstance(asset_info.confidence, (int, float)):
                conf_str = f"{asset_info.confidence:.2%}"
            else:
                conf_str = asset_info.confidence

            self.logger.info(
                f"✓ Asset identified: {asset_info.vendor} {asset_info.os_type} "
                f"({asset_info.device_type}) - Confidence: {conf_str}"
            )

            return asset_info

        except ValidationError as e:
            self.logger.error(f"Response validation failed: {str(e)}")
            self.logger.debug(f"Raw response: {response.content[:500]}...")
            raise
        except Exception as e:
            self.logger.error(f"Asset identification failed: {str(e)}")
            raise

    def analyze_from_file(self, config_file: Path) -> AssetInfo:
        """
        Analyze configuration file to identify asset.

        Args:
            config_file: Path to configuration file

        Returns:
            AssetInfo: Identified asset information
        """
        self.logger.info(f"Reading configuration from: {config_file}")

        try:
            config = FileHandler.read_text(config_file)
            return self.analyze(config)
        except FileNotFoundError as e:
            self.logger.error(f"Configuration file not found: {config_file}")
            raise


def identify_asset(
    config: str,
    ai_client: BaseAIClient,
    templates_dir: Optional[Path] = None
) -> AssetInfo:
    """
    Convenience function to identify asset from configuration.

    Args:
        config: Device configuration text
        ai_client: AI client instance
        templates_dir: Optional custom templates directory

    Returns:
        AssetInfo: Identified asset information
    """
    stage = AssetIdentificationStage(ai_client, templates_dir)
    return stage.analyze(config)
