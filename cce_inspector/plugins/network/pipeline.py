"""
Network CCE Assessment Pipeline

Orchestrates the complete 4-stage assessment workflow for network devices.
"""

import time
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from cce_inspector.core.ai_clients.base import BaseAIClient
from cce_inspector.core.ai_clients.factory import create_ai_client
from cce_inspector.core.config import CCEConfig, get_config
from cce_inspector.core.utils import get_logger, FileHandler, configure_logger_from_config

from .stages.stage1_asset import AssetIdentificationStage, AssetInfo
from .stages.stage2_criteria import CriteriaMappingStage, CriteriaMappingResult
from .stages.stage3_parsing import ConfigParsingStage, ConfigParsingResult
from .stages.stage4_assessment import VulnerabilityAssessmentStage, VulnerabilityAssessmentResult


@dataclass
class PipelineResult:
    """
    Complete pipeline execution result.

    Attributes:
        asset_info: Asset identification result
        criteria_result: Criteria mapping result
        parsing_result: Configuration parsing result
        assessment_result: Vulnerability assessment result
        execution_time: Total execution time in seconds
        timestamp: Execution timestamp
        metadata: Additional metadata
    """
    asset_info: AssetInfo
    criteria_result: CriteriaMappingResult
    parsing_result: ConfigParsingResult
    assessment_result: VulnerabilityAssessmentResult
    execution_time: float
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'timestamp': self.timestamp,
            'execution_time_seconds': self.execution_time,
            'asset_info': self.asset_info.to_dict(),
            'criteria_mapping': self.criteria_result.to_dict(),
            'config_parsing': self.parsing_result.to_dict(),
            'vulnerability_assessment': self.assessment_result.to_dict(),
            'summary': self.assessment_result.get_summary(),
            'metadata': self.metadata
        }


class NetworkCCEPipeline:
    """
    Complete CCE assessment pipeline for network devices.

    Coordinates execution of all 4 stages:
    1. Asset Identification
    2. Criteria Mapping
    3. Configuration Parsing
    4. Vulnerability Assessment
    """

    def __init__(
        self,
        config: Optional[CCEConfig] = None,
        ai_client: Optional[BaseAIClient] = None
    ):
        """
        Initialize pipeline.

        Args:
            config: Optional CCEConfig instance (loads from env if not provided)
            ai_client: Optional AI client (creates from config if not provided)
        """
        # Load configuration
        self.config = config or get_config()

        # Configure logger
        self.logger = configure_logger_from_config(self.config)

        # Create or use provided AI client
        self.ai_client = ai_client or create_ai_client(self.config)

        # Initialize stages
        self.stage1 = AssetIdentificationStage(self.ai_client)
        self.stage2 = CriteriaMappingStage(self.ai_client)
        self.stage3 = ConfigParsingStage(self.ai_client)
        self.stage4 = VulnerabilityAssessmentStage(self.ai_client)

        self.logger.info("Network CCE Pipeline initialized")
        self.logger.info(f"AI Provider: {self.config.ai_provider}")
        self.logger.info(f"Output Format: {self.config.output_format}")

    def run(
        self,
        config_text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PipelineResult:
        """
        Execute complete CCE assessment pipeline.

        Args:
            config_text: Device configuration text (e.g., show running-config)
            metadata: Optional metadata to include in result

        Returns:
            PipelineResult: Complete assessment result

        Raises:
            Exception: If any stage fails
        """
        start_time = time.time()
        timestamp = datetime.now().isoformat()

        self.logger.info("=" * 80)
        self.logger.info("Starting CCE Assessment Pipeline")
        self.logger.info("=" * 80)

        try:
            # Stage 1: Asset Identification
            asset_info = self.stage1.analyze(config_text)
            stage1_time = time.time() - start_time
            self.logger.stage_complete("Stage 1: Asset Identification", stage1_time)

            # Stage 2: Criteria Mapping
            stage2_start = time.time()
            criteria_result = self.stage2.map_criteria(asset_info, config_text)
            stage2_time = time.time() - stage2_start
            self.logger.stage_complete("Stage 2: Criteria Mapping", stage2_time)

            # Stage 3: Configuration Parsing
            stage3_start = time.time()
            parsing_result = self.stage3.parse_config(config_text, asset_info, criteria_result)
            stage3_time = time.time() - stage3_start
            self.logger.stage_complete("Stage 3: Configuration Parsing", stage3_time)

            # Stage 4: Vulnerability Assessment
            stage4_start = time.time()
            assessment_result = self.stage4.assess(asset_info, criteria_result, parsing_result)
            stage4_time = time.time() - stage4_start
            self.logger.stage_complete("Stage 4: Vulnerability Assessment", stage4_time)

            # Calculate total time
            execution_time = time.time() - start_time

            # Build metadata
            full_metadata = metadata or {}
            full_metadata.update({
                'ai_provider': self.config.ai_provider,
                'stage_timings': {
                    'stage1_seconds': stage1_time,
                    'stage2_seconds': stage2_time,
                    'stage3_seconds': stage3_time,
                    'stage4_seconds': stage4_time
                }
            })

            # Create result
            result = PipelineResult(
                asset_info=asset_info,
                criteria_result=criteria_result,
                parsing_result=parsing_result,
                assessment_result=assessment_result,
                execution_time=execution_time,
                timestamp=timestamp,
                metadata=full_metadata
            )

            self.logger.info("=" * 80)
            self.logger.info(f"Pipeline completed successfully in {execution_time:.2f} seconds")
            self.logger.info("=" * 80)

            return result

        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}")
            self.logger.exception("Full traceback:")
            raise

    def run_from_file(
        self,
        config_file: Path,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PipelineResult:
        """
        Execute pipeline from configuration file.

        Args:
            config_file: Path to configuration file
            metadata: Optional metadata

        Returns:
            PipelineResult: Assessment result
        """
        self.logger.info(f"Loading configuration from: {config_file}")

        try:
            config_text = FileHandler.read_text(config_file)

            # Add file info to metadata
            file_metadata = metadata or {}
            file_metadata['source_file'] = str(config_file)
            file_metadata['file_size_bytes'] = config_file.stat().st_size

            return self.run(config_text, file_metadata)

        except FileNotFoundError as e:
            self.logger.error(f"Configuration file not found: {config_file}")
            raise

    def save_result(
        self,
        result: PipelineResult,
        output_dir: Optional[Path] = None,
        format: str = "json"
    ) -> Path:
        """
        Save assessment result to file.

        Args:
            result: Pipeline result
            output_dir: Output directory (uses config default if not specified)
            format: Output format ('json', 'html', or 'both')

        Returns:
            Path: Path to saved JSON file
        """
        output_dir = output_dir or self.config.output_dir

        # Save JSON
        json_path = FileHandler.save_assessment_result(
            output_dir,
            result.asset_info.hostname,
            result.to_dict(),
            format="json"
        )

        self.logger.info(f"Assessment result saved: {json_path}")

        # TODO: Save HTML report when report generator is implemented
        if format in ("html", "both"):
            self.logger.warning("HTML report generation not yet implemented")

        return json_path


def run_network_assessment(
    config_text: str,
    config: Optional[CCEConfig] = None,
    save_output: bool = True
) -> PipelineResult:
    """
    Convenience function to run complete network assessment.

    Args:
        config_text: Device configuration text
        config: Optional CCEConfig instance
        save_output: Whether to save output to file

    Returns:
        PipelineResult: Assessment result

    Example:
        >>> with open('router_config.txt', 'r') as f:
        ...     config = f.read()
        >>> result = run_network_assessment(config)
        >>> print(f"Assessment: {result.assessment_result.get_summary()}")
    """
    pipeline = NetworkCCEPipeline(config)
    result = pipeline.run(config_text)

    if save_output:
        pipeline.save_result(result)

    return result
