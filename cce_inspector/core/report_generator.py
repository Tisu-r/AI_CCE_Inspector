"""
HTML Report Generator

Generates professional HTML reports from assessment results using Jinja2 templates.
"""

from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, Template

from .utils import FileHandler, get_logger


class ReportGenerator:
    """
    Generates HTML reports from CCE assessment results.
    """

    def __init__(self, templates_dir: Path = None):
        """
        Initialize report generator.

        Args:
            templates_dir: Optional custom templates directory
        """
        if templates_dir is None:
            # Default to project templates/reports directory
            templates_dir = Path(__file__).parent.parent / "templates" / "reports"

        self.templates_dir = templates_dir
        self.logger = get_logger()

        # Setup Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=True
        )

        # Add custom filters
        self.env.filters['percentage'] = self._percentage_filter
        self.env.filters['severity_badge'] = self._severity_badge_filter
        self.env.filters['status_badge'] = self._status_badge_filter

    @staticmethod
    def _percentage_filter(value: float) -> str:
        """Format number as percentage."""
        return f"{value:.1f}%"

    @staticmethod
    def _severity_badge_filter(severity: str) -> str:
        """Get CSS class for severity badge."""
        severity_map = {
            'critical': 'badge-critical',
            'high': 'badge-danger',
            'medium': 'badge-warning',
            'low': 'badge-info',
            'info': 'badge-success'
        }
        return severity_map.get(severity.lower(), 'badge-secondary')

    @staticmethod
    def _status_badge_filter(status: str) -> str:
        """Get CSS class for status badge."""
        status_map = {
            'pass': 'badge-success',
            'fail': 'badge-danger',
            'manual_review': 'badge-warning'
        }
        return status_map.get(status.lower(), 'badge-secondary')

    def _prepare_report_data(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare and format data for report template.

        Args:
            assessment_data: Raw assessment result dictionary

        Returns:
            Dict with formatted data for template
        """
        # Extract asset information
        asset_info = assessment_data.get('asset_info', {})

        # Extract summary
        summary = assessment_data.get('summary', {})

        # Extract assessment results
        assessment_results = assessment_data.get(
            'vulnerability_assessment', {}
        ).get('assessment_results', {})

        # Group findings by severity (we'll need to load baseline for severity info)
        findings_by_severity = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': [],
            'info': []
        }

        # Get critical findings (failed checks)
        critical_findings = []

        for check_id, result in assessment_results.items():
            finding = {
                'check_id': check_id,
                'status': result['status'],
                'score': result['score'],
                'findings': result['findings'],
                'recommendation': result['recommendation'],
                'remediation_commands': result.get('remediation_commands', []),
                'severity': 'high'  # Default severity, should load from baseline
            }

            if result['status'] == 'fail':
                critical_findings.append(finding)

        # Sort critical findings by score (lower score = more critical)
        critical_findings.sort(key=lambda x: x['score'])

        # Prepare final data structure
        report_data = {
            'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'asset_info': {
                'hostname': asset_info.get('hostname', 'Unknown'),
                'vendor': asset_info.get('vendor', 'Unknown'),
                'os_type': asset_info.get('os_type', 'Unknown'),
                'os_version': asset_info.get('os_version', 'Unknown'),
                'device_type': asset_info.get('device_type', 'Unknown'),
                'device_role': asset_info.get('device_role', 'Unknown'),
                'confidence': asset_info.get('confidence', 0.0)
            },
            'summary': {
                'total_checks': summary.get('total_checks', 0),
                'passed': summary.get('passed', 0),
                'failed': summary.get('failed', 0),
                'manual_review': summary.get('manual_review', 0),
                'pass_percentage': summary.get('pass_percentage', 0.0),
                'fail_percentage': summary.get('fail_percentage', 0.0),
                'average_score': summary.get('average_score', 0.0)
            },
            'critical_findings': critical_findings[:10],  # Top 10 critical findings
            'findings_by_category': findings_by_severity,
            'all_findings': [
                {
                    'check_id': check_id,
                    **result
                }
                for check_id, result in assessment_results.items()
            ],
            'execution_time': assessment_data.get('execution_time_seconds', 0),
            'timestamp': assessment_data.get('timestamp', datetime.now().isoformat()),
            'metadata': assessment_data.get('metadata', {})
        }

        return report_data

    def generate_html(
        self,
        assessment_data: Dict[str, Any],
        template_name: str = "html_report.jinja2"
    ) -> str:
        """
        Generate HTML report from assessment data.

        Args:
            assessment_data: Assessment result dictionary
            template_name: Template filename

        Returns:
            str: Generated HTML content
        """
        try:
            # Prepare data
            self.logger.info("Preparing report data...")
            report_data = self._prepare_report_data(assessment_data)

            # Load template
            self.logger.info(f"Loading template: {template_name}")
            template = self.env.get_template(template_name)

            # Render template
            self.logger.info("Rendering HTML report...")
            html_content = template.render(**report_data)

            self.logger.info("HTML report generated successfully")
            return html_content

        except Exception as e:
            self.logger.error(f"Failed to generate HTML report: {str(e)}")
            raise

    def save_html_report(
        self,
        assessment_data: Dict[str, Any],
        output_path: Path,
        template_name: str = "html_report.jinja2"
    ) -> Path:
        """
        Generate and save HTML report to file.

        Args:
            assessment_data: Assessment result dictionary
            output_path: Output file path
            template_name: Template filename

        Returns:
            Path: Path to saved report
        """
        try:
            # Generate HTML
            html_content = self.generate_html(assessment_data, template_name)

            # Save to file
            FileHandler.write_text(output_path, html_content)

            self.logger.info(f"HTML report saved: {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Failed to save HTML report: {str(e)}")
            raise

    def generate_summary_report(
        self,
        assessment_results: List[Dict[str, Any]]
    ) -> str:
        """
        Generate summary report for multiple assessments.

        Args:
            assessment_results: List of assessment result dictionaries

        Returns:
            str: Generated HTML content

        TODO: Implement multi-assessment summary template
        """
        raise NotImplementedError("Summary report for multiple assessments not yet implemented")


def generate_html_report(
    assessment_data: Dict[str, Any],
    output_path: Path,
    templates_dir: Path = None
) -> Path:
    """
    Convenience function to generate HTML report.

    Args:
        assessment_data: Assessment result dictionary
        output_path: Output file path
        templates_dir: Optional custom templates directory

    Returns:
        Path: Path to saved report

    Example:
        >>> result = pipeline.run(config)
        >>> report_path = generate_html_report(
        ...     result.to_dict(),
        ...     Path("output/report.html")
        ... )
    """
    generator = ReportGenerator(templates_dir)
    return generator.save_html_report(assessment_data, output_path)
