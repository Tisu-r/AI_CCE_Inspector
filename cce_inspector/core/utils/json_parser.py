"""
JSON parsing utilities with error recovery.

Provides robust JSON parsing with automatic cleanup and error recovery.
"""

import json
import re
from typing import Dict, Any, Optional


class JSONParser:
    """
    Robust JSON parser with error recovery capabilities.
    """

    @staticmethod
    def extract_json(text: str) -> str:
        """
        Extract JSON from text that may contain markdown code blocks or other formatting.

        Args:
            text: Raw text potentially containing JSON

        Returns:
            str: Extracted JSON string

        Raises:
            ValueError: If no JSON-like content found
        """
        # Remove leading/trailing whitespace
        text = text.strip()

        # Try to extract from markdown code blocks
        json_patterns = [
            r'```json\s*\n(.*?)\n```',  # ```json ... ```
            r'```\s*\n(.*?)\n```',      # ``` ... ```
            r'`(.*?)`',                 # ` ... `
        ]

        for pattern in json_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                text = match.group(1).strip()
                break

        # If text doesn't start with { or [, try to find JSON object
        if not text.startswith(('{', '[')):
            # Look for first { or [
            json_start = -1
            for char in ['{', '[']:
                pos = text.find(char)
                if pos != -1 and (json_start == -1 or pos < json_start):
                    json_start = pos

            if json_start != -1:
                text = text[json_start:]

        if not text:
            raise ValueError("No JSON-like content found in text")

        return text

    @staticmethod
    def clean_json_string(text: str) -> str:
        """
        Clean JSON string by removing common issues.

        Args:
            text: JSON string to clean

        Returns:
            str: Cleaned JSON string
        """
        # Remove BOM if present
        text = text.lstrip('\ufeff')

        # Remove control characters except newline, tab, carriage return
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', text)

        # Fix common JSON issues
        # Replace single quotes with double quotes (be careful with this)
        # Only do this for keys, not all single quotes
        text = re.sub(r"(\w+)':", r'\1":', text)  # word': -> word":
        text = re.sub(r"'(\w+)\":", r'"\1":', text)  # 'word": -> "word":

        # Remove trailing commas before closing braces/brackets
        text = re.sub(r',(\s*[}\]])', r'\1', text)

        return text

    @staticmethod
    def parse(text: str, strict: bool = True) -> Dict[str, Any]:
        """
        Parse JSON with automatic cleanup and error recovery.

        Args:
            text: Text containing JSON
            strict: If False, attempt more aggressive cleanup

        Returns:
            Dict: Parsed JSON object

        Raises:
            json.JSONDecodeError: If parsing fails after all recovery attempts
        """
        # First attempt: parse as-is
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Second attempt: extract and clean
        try:
            extracted = JSONParser.extract_json(text)
            cleaned = JSONParser.clean_json_string(extracted)
            return json.loads(cleaned)
        except (json.JSONDecodeError, ValueError):
            pass

        # Third attempt: more aggressive cleanup (if not strict)
        if not strict:
            try:
                # Remove comments (// and /* */)
                text_no_comments = re.sub(r'//.*?$', '', text, flags=re.MULTILINE)
                text_no_comments = re.sub(r'/\*.*?\*/', '', text_no_comments, flags=re.DOTALL)

                extracted = JSONParser.extract_json(text_no_comments)
                cleaned = JSONParser.clean_json_string(extracted)

                # Try to fix unquoted keys
                cleaned = re.sub(r'(\s*)(\w+)(\s*):', r'\1"\2"\3:', cleaned)

                return json.loads(cleaned)
            except (json.JSONDecodeError, ValueError):
                pass

        # If all attempts fail, raise the original error
        raise json.JSONDecodeError(
            "Failed to parse JSON after all recovery attempts",
            text[:100],  # Show first 100 chars in error
            0
        )

    @staticmethod
    def safe_parse(text: str, default: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Safely parse JSON, returning default value on failure.

        Args:
            text: Text containing JSON
            default: Default value to return on failure (None if not specified)

        Returns:
            Parsed JSON or default value
        """
        try:
            return JSONParser.parse(text, strict=False)
        except json.JSONDecodeError:
            return default

    @staticmethod
    def validate_and_parse(text: str, required_keys: list = None) -> Dict[str, Any]:
        """
        Parse JSON and validate that required keys are present.

        Args:
            text: Text containing JSON
            required_keys: List of required keys in parsed object

        Returns:
            Dict: Parsed and validated JSON object

        Raises:
            json.JSONDecodeError: If parsing fails
            ValueError: If required keys are missing
        """
        data = JSONParser.parse(text)

        if required_keys:
            missing_keys = [key for key in required_keys if key not in data]
            if missing_keys:
                raise ValueError(f"Missing required keys: {', '.join(missing_keys)}")

        return data

    @staticmethod
    def pretty_print(data: Dict[str, Any], indent: int = 2) -> str:
        """
        Convert Python dict to pretty-printed JSON string.

        Args:
            data: Dictionary to convert
            indent: Indentation level

        Returns:
            str: Formatted JSON string
        """
        return json.dumps(data, indent=indent, ensure_ascii=False)

    @staticmethod
    def minify(text: str) -> str:
        """
        Parse JSON and return minified version.

        Args:
            text: JSON text to minify

        Returns:
            str: Minified JSON string

        Raises:
            json.JSONDecodeError: If parsing fails
        """
        data = JSONParser.parse(text)
        return json.dumps(data, separators=(',', ':'), ensure_ascii=False)
