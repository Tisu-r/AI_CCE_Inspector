"""
Stage 4: Vulnerability Assessment

Evaluates parsed configuration against CCE criteria to determine
Pass/Fail status and provide remediation recommendations.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Literal
from dataclasses import dataclass, field

from cce_inspector.core.ai_clients.base import BaseAIClient, AIResponse
from cce_inspector.core.validators import ResponseValidator, ValidationError, Stage
from cce_inspector.core.utils import FileHandler, JSONParser, get_logger

from .stage1_asset import AssetInfo
from .stage2_criteria import CriteriaMappingResult
from .stage3_parsing import ConfigParsingResult


@dataclass
class AssessmentResult:
    """
    Assessment result for a single check.

    Attributes:
        check_id: CCE check identifier
        status: Assessment status ('pass', 'fail', 'manual_review')
        score: Score (0-100)
        findings: Description of findings
        recommendation: Recommendation for remediation
        remediation_commands: List of commands to fix the issue
    """
    check_id: str
    status: Literal['pass', 'fail', 'manual_review']
    score: float
    findings: str
    recommendation: str
    remediation_commands: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, check_id: str, data: Dict[str, Any]) -> 'AssessmentResult':
        """Create AssessmentResult from dictionary."""
        return cls(
            check_id=check_id,
            status=data['status'],
            score=data['score'],
            findings=data['findings'],
            recommendation=data['recommendation'],
            remediation_commands=data.get('remediation_commands', [])
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'status': self.status,
            'score': self.score,
            'findings': self.findings,
            'recommendation': self.recommendation,
            'remediation_commands': self.remediation_commands
        }


@dataclass
class VulnerabilityAssessmentResult:
    """
    Complete vulnerability assessment result.

    Attributes:
        assessment_results: Dictionary mapping check_id to assessment result
    """
    assessment_results: Dict[str, AssessmentResult] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VulnerabilityAssessmentResult':
        """Create VulnerabilityAssessmentResult from dictionary."""
        assessment_results = {}
        for check_id, result_data in data.get('assessment_results', {}).items():
            assessment_results[check_id] = AssessmentResult.from_dict(check_id, result_data)

        return cls(assessment_results=assessment_results)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'assessment_results': {
                check_id: result.to_dict()
                for check_id, result in self.assessment_results.items()
            }
        }

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of the assessment.

        Returns:
            Dict with total, passed, failed, manual_review counts and percentages
        """
        total = len(self.assessment_results)
        passed = sum(1 for r in self.assessment_results.values() if r.status == 'pass')
        failed = sum(1 for r in self.assessment_results.values() if r.status == 'fail')
        manual = sum(1 for r in self.assessment_results.values() if r.status == 'manual_review')

        avg_score = sum(r.score for r in self.assessment_results.values()) / total if total > 0 else 0

        return {
            'total_checks': total,
            'passed': passed,
            'failed': failed,
            'manual_review': manual,
            'pass_percentage': (passed / total * 100) if total > 0 else 0,
            'fail_percentage': (failed / total * 100) if total > 0 else 0,
            'average_score': avg_score
        }

    def get_critical_findings(self) -> List[AssessmentResult]:
        """Get all failed checks sorted by severity (assuming lower score = higher severity)."""
        return sorted(
            [r for r in self.assessment_results.values() if r.status == 'fail'],
            key=lambda x: x.score
        )


class VulnerabilityAssessmentStage:
    """
    Stage 4: Assess vulnerabilities based on parsed configuration.
    """

    def __init__(
        self,
        ai_client: BaseAIClient,
        baseline_file: str = "cce_baseline.json",
        templates_dir: Optional[Path] = None
    ):
        """
        Initialize Stage 4.

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
        Load Stage 4 prompt template.

        Returns:
            str: Prompt template content
        """
        try:
            return FileHandler.load_prompt_template(
                "stage4_vulnerability_assessment",
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

    def _get_check_details(
        self,
        check_id: str,
        cce_baseline: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed check information from baseline.

        Args:
            check_id: CCE check identifier
            cce_baseline: CCE baseline data

        Returns:
            Check details dict or None if not found
        """
        for check in cce_baseline:
            if check['check_id'] == check_id:
                return check
        return None

    def _build_prompt(
        self,
        asset_info: AssetInfo,
        parsing_result: ConfigParsingResult,
        cce_baseline: List[Dict[str, Any]]
    ) -> str:
        """
        Build prompt for vulnerability assessment.

        Args:
            asset_info: Asset identification information
            parsing_result: Configuration parsing result
            cce_baseline: CCE baseline data

        Returns:
            str: Complete prompt
        """
        template = self._load_prompt_template()

        # Format asset information
        asset_json = JSONParser.pretty_print(asset_info.to_dict())

        # Format parsed configuration
        parsed_json = JSONParser.pretty_print(parsing_result.to_dict())

        # Format CCE baseline with evaluation criteria
        checks_with_criteria = []
        for check_id in parsing_result.parsed_config.keys():
            check_details = self._get_check_details(check_id, cce_baseline)
            if check_details:
                checks_with_criteria.append({
                    "check_id": check_details["check_id"],
                    "title": check_details["title"],
                    "severity": check_details["severity"],
                    "check_patterns": check_details.get("check_patterns", {}),
                    "evaluation_criteria": check_details.get("evaluation_criteria", {}),
                    "vendor_commands": check_details.get("vendor_commands", {})
                })

        criteria_json = JSONParser.pretty_print(checks_with_criteria)

        # Replace placeholders
        prompt = template.replace("{{ASSET_INFO}}", asset_json)
        prompt = prompt.replace("{{PARSED_CONFIG}}", parsed_json)
        prompt = prompt.replace("{{CCE_CRITERIA}}", criteria_json)

        return prompt

    def assess(
        self,
        asset_info: AssetInfo,
        criteria_result: CriteriaMappingResult,
        parsing_result: ConfigParsingResult
    ) -> VulnerabilityAssessmentResult:
        """
        Assess vulnerabilities based on parsed configuration.

        Args:
            asset_info: Asset identification information
            criteria_result: Criteria mapping result from Stage 2
            parsing_result: Configuration parsing result from Stage 3

        Returns:
            VulnerabilityAssessmentResult: Assessment results

        Raises:
            ValidationError: If AI response validation fails
            Exception: If AI request fails
        """
        self.logger.stage_start("Vulnerability Assessment", 4)

        try:
            # Load CCE baseline
            self.logger.info("Loading CCE baseline for assessment...")
            cce_baseline = self._load_cce_baseline()

            # Build prompt
            prompt = self._build_prompt(asset_info, parsing_result, cce_baseline)

            # Get AI response
            self.logger.info("Performing vulnerability assessment...")
            response: AIResponse = self.ai_client.generate(
                prompt=prompt,
                system_prompt="You are a network security auditor assessing compliance vulnerabilities."
            )

            self.logger.debug(f"AI response received ({response.tokens_used.get('total', 0)} tokens)")

            # Validate and parse response
            self.logger.info("Validating assessment response...")
            validated_data = ResponseValidator.validate_stage(
                Stage.VULNERABILITY_ASSESSMENT,
                response.content
            )

            # Convert to result object
            result = VulnerabilityAssessmentResult.from_dict(validated_data)

            # Get summary and log results
            summary = result.get_summary()

            self.logger.info(
                f"✓ Assessment complete: {summary['passed']}/{summary['total_checks']} passed "
                f"({summary['pass_percentage']:.1f}%)"
            )

            # Log individual check results
            for check_id, assessment in result.assessment_results.items():
                self.logger.check_result(
                    check_id,
                    assessment.status,
                    f"{assessment.score:.0f}/100"
                )

            # Log summary
            self.logger.summary(
                summary['total_checks'],
                summary['passed'],
                summary['failed'],
                summary['manual_review']
            )

            return result

        except ValidationError as e:
            self.logger.error(f"Response validation failed: {str(e)}")
            self.logger.debug(f"Raw response: {response.content[:500]}...")
            raise
        except Exception as e:
            self.logger.error(f"Vulnerability assessment failed: {str(e)}")
            raise


def assess_vulnerabilities(
    asset_info: AssetInfo,
    criteria_result: CriteriaMappingResult,
    parsing_result: ConfigParsingResult,
    ai_client: BaseAIClient,
    templates_dir: Optional[Path] = None
) -> VulnerabilityAssessmentResult:
    """
    Convenience function to assess vulnerabilities.

    Args:
        asset_info: Asset identification information
        criteria_result: Criteria mapping result
        parsing_result: Configuration parsing result
        ai_client: AI client instance
        templates_dir: Optional custom templates directory

    Returns:
        VulnerabilityAssessmentResult: Assessment result
    """
    stage = VulnerabilityAssessmentStage(ai_client, templates_dir=templates_dir)
    return stage.assess(asset_info, criteria_result, parsing_result)
