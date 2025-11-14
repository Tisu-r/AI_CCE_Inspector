"""
JSON schema validators for AI responses.

Validates that AI responses conform to expected schemas for each assessment stage.
"""

import json
from typing import Dict, Any, Optional, List
from enum import Enum


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class Stage(Enum):
    """Assessment stage identifiers."""
    ASSET_IDENTIFICATION = "stage1"
    CRITERIA_MAPPING = "stage2"
    CONFIG_PARSING = "stage3"
    VULNERABILITY_ASSESSMENT = "stage4"


class ResponseValidator:
    """
    Validates AI responses against expected schemas for each stage.
    """

    @staticmethod
    def validate_json_format(response_text: str) -> Dict[str, Any]:
        """
        Validate that response is valid JSON.

        Args:
            response_text: Raw response text from AI

        Returns:
            Dict: Parsed JSON object

        Raises:
            ValidationError: If response is not valid JSON
        """
        try:
            # Try to extract JSON if wrapped in markdown code blocks
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON format: {str(e)}")

    @staticmethod
    def validate_stage1_asset_identification(data: Dict[str, Any]) -> None:
        """
        Validate Stage 1: Asset Identification response.

        Expected schema:
        {
            "vendor": str,
            "os_type": str,
            "os_version": str,
            "hostname": str,
            "device_type": str,
            "device_role": str,
            "confidence": float
        }

        Args:
            data: Parsed JSON response

        Raises:
            ValidationError: If schema validation fails
        """
        required_fields = [
            "vendor", "os_type", "os_version", "hostname",
            "device_type", "device_role", "confidence"
        ]

        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")

        # Validate confidence (can be number 0-1 or string high/medium/low)
        confidence = data.get("confidence")
        if isinstance(confidence, str):
            # Accept string values: high, medium, low
            if confidence.lower() not in ["high", "medium", "low"]:
                raise ValidationError("Confidence string must be 'high', 'medium', or 'low'")
        elif isinstance(confidence, (int, float)):
            # Accept numeric values 0-1
            if not (0 <= confidence <= 1):
                raise ValidationError("Confidence number must be between 0 and 1")
        else:
            raise ValidationError("Confidence must be a number (0-1) or string (high/medium/low)")

        # Validate string fields are not empty
        string_fields = ["vendor", "os_type", "device_type", "device_role"]
        for field in string_fields:
            if not isinstance(data[field], str) or len(data[field].strip()) == 0:
                raise ValidationError(f"{field} must be a non-empty string")

    @staticmethod
    def validate_stage2_criteria_mapping(data: Dict[str, Any]) -> None:
        """
        Validate Stage 2: Criteria Mapping response.

        Expected schema:
        {
            "applicable_checks": [
                {
                    "check_id": str,
                    "reason": str
                }
            ],
            "excluded_checks": [
                {
                    "check_id": str,
                    "reason": str
                }
            ]
        }

        Args:
            data: Parsed JSON response

        Raises:
            ValidationError: If schema validation fails
        """
        if "applicable_checks" not in data:
            raise ValidationError("Missing required field: applicable_checks")
        if "excluded_checks" not in data:
            raise ValidationError("Missing required field: excluded_checks")

        # Validate applicable_checks
        if not isinstance(data["applicable_checks"], list):
            raise ValidationError("applicable_checks must be an array")

        for check in data["applicable_checks"]:
            if not isinstance(check, dict):
                raise ValidationError("Each applicable check must be an object")
            if "check_id" not in check or "reason" not in check:
                raise ValidationError("Each applicable check must have check_id and reason")

        # Validate excluded_checks
        if not isinstance(data["excluded_checks"], list):
            raise ValidationError("excluded_checks must be an array")

        for check in data["excluded_checks"]:
            if not isinstance(check, dict):
                raise ValidationError("Each excluded check must be an object")
            if "check_id" not in check or "reason" not in check:
                raise ValidationError("Each excluded check must have check_id and reason")

    @staticmethod
    def validate_stage3_config_parsing(data: Dict[str, Any]) -> None:
        """
        Validate Stage 3: Configuration Parsing response.

        Expected schema:
        {
            "parsed_config": {
                "check_id": {
                    "found_config": [str],
                    "extracted_values": dict,
                    "config_present": bool
                }
            }
        }

        Args:
            data: Parsed JSON response

        Raises:
            ValidationError: If schema validation fails
        """
        if "parsed_config" not in data:
            raise ValidationError("Missing required field: parsed_config")

        if not isinstance(data["parsed_config"], dict):
            raise ValidationError("parsed_config must be an object")

        # Validate each check result
        for check_id, check_data in data["parsed_config"].items():
            if not isinstance(check_data, dict):
                raise ValidationError(f"Check {check_id} data must be an object")

            required = ["found_config", "extracted_values", "config_present"]
            for field in required:
                if field not in check_data:
                    raise ValidationError(f"Check {check_id} missing field: {field}")

            if not isinstance(check_data["found_config"], list):
                raise ValidationError(f"Check {check_id} found_config must be an array")

            if not isinstance(check_data["extracted_values"], dict):
                raise ValidationError(f"Check {check_id} extracted_values must be an object")

            if not isinstance(check_data["config_present"], bool):
                raise ValidationError(f"Check {check_id} config_present must be a boolean")

    @staticmethod
    def validate_stage4_vulnerability_assessment(data: Dict[str, Any]) -> None:
        """
        Validate Stage 4: Vulnerability Assessment response.

        Expected schema:
        {
            "assessment_results": {
                "check_id": {
                    "status": "pass" | "fail" | "manual_review",
                    "score": float,
                    "findings": str,
                    "recommendation": str,
                    "remediation_commands": [str]
                }
            }
        }

        Args:
            data: Parsed JSON response

        Raises:
            ValidationError: If schema validation fails
        """
        if "assessment_results" not in data:
            raise ValidationError("Missing required field: assessment_results")

        assessment_results = data["assessment_results"]

        # Accept both dict (old format) and list (new format from Claude)
        if isinstance(assessment_results, list):
            # Convert list to dict keyed by check_id
            results_dict = {}
            for result in assessment_results:
                if not isinstance(result, dict):
                    raise ValidationError("Each assessment result must be an object")
                if "check_id" not in result:
                    raise ValidationError("Each assessment result must have check_id")
                results_dict[result["check_id"]] = result
            assessment_results = results_dict
        elif not isinstance(assessment_results, dict):
            raise ValidationError("assessment_results must be an object or array")

        valid_statuses = ["pass", "fail", "manual_review", "not_configured"]  # Added not_configured

        # Validate each assessment result
        for check_id, result in assessment_results.items():
            if not isinstance(result, dict):
                raise ValidationError(f"Check {check_id} result must be an object")

            required = ["status", "score", "findings", "recommendation", "remediation_commands"]
            for field in required:
                if field not in result:
                    raise ValidationError(f"Check {check_id} missing field: {field}")

            # Validate status (case-insensitive)
            status = result["status"].lower() if isinstance(result["status"], str) else result["status"]
            if status not in valid_statuses:
                raise ValidationError(
                    f"Check {check_id} invalid status: {result['status']}. "
                    f"Must be one of: {', '.join(valid_statuses)}"
                )
            # Normalize to lowercase
            result["status"] = status

            # Validate score
            score = result["score"]
            if not isinstance(score, (int, float)) or not (0 <= score <= 100):
                raise ValidationError(f"Check {check_id} score must be a number between 0 and 100")

            # Validate remediation_commands is array
            if not isinstance(result["remediation_commands"], list):
                raise ValidationError(f"Check {check_id} remediation_commands must be an array")

        # Return normalized dict format
        data["assessment_results"] = assessment_results

    @staticmethod
    def validate_stage(stage: Stage, response_text: str) -> Dict[str, Any]:
        """
        Validate response for a specific stage.

        Args:
            stage: Assessment stage identifier
            response_text: Raw response text from AI

        Returns:
            Dict: Validated and parsed JSON data

        Raises:
            ValidationError: If validation fails
        """
        # First, validate JSON format
        data = ResponseValidator.validate_json_format(response_text)

        # Then, validate stage-specific schema
        validators = {
            Stage.ASSET_IDENTIFICATION: ResponseValidator.validate_stage1_asset_identification,
            Stage.CRITERIA_MAPPING: ResponseValidator.validate_stage2_criteria_mapping,
            Stage.CONFIG_PARSING: ResponseValidator.validate_stage3_config_parsing,
            Stage.VULNERABILITY_ASSESSMENT: ResponseValidator.validate_stage4_vulnerability_assessment
        }

        validator = validators.get(stage)
        if validator:
            validator(data)

        return data


class CCECheckValidator:
    """
    Validates CCE check definitions and baseline files.
    """

    @staticmethod
    def validate_check_definition(check: Dict[str, Any]) -> None:
        """
        Validate a single CCE check definition.

        Args:
            check: Check definition dictionary

        Raises:
            ValidationError: If check definition is invalid
        """
        required_fields = ["check_id", "title", "severity", "check_patterns"]

        for field in required_fields:
            if field not in check:
                raise ValidationError(f"Check missing required field: {field}")

        # Validate severity
        valid_severities = ["critical", "high", "medium", "low", "info"]
        if check["severity"] not in valid_severities:
            raise ValidationError(
                f"Invalid severity: {check['severity']}. "
                f"Must be one of: {', '.join(valid_severities)}"
            )

        # Validate check_patterns
        patterns = check.get("check_patterns", {})
        if not isinstance(patterns, dict):
            raise ValidationError("check_patterns must be an object")

    @staticmethod
    def validate_baseline(baseline: List[Dict[str, Any]]) -> None:
        """
        Validate entire CCE baseline file.

        Args:
            baseline: List of check definitions

        Raises:
            ValidationError: If baseline is invalid
        """
        if not isinstance(baseline, list):
            raise ValidationError("Baseline must be an array of checks")

        check_ids = set()
        for check in baseline:
            CCECheckValidator.validate_check_definition(check)

            # Check for duplicate IDs
            check_id = check["check_id"]
            if check_id in check_ids:
                raise ValidationError(f"Duplicate check_id: {check_id}")
            check_ids.add(check_id)
