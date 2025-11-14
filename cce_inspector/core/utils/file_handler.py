"""
File handling utilities for CCE Inspector.

Handles reading/writing configuration files, reports, and cached data.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime


class FileHandler:
    """
    Utility class for file operations.
    """

    @staticmethod
    def read_text(file_path: Path) -> str:
        """
        Read text file.

        Args:
            file_path: Path to file

        Returns:
            str: File contents

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file cannot be read
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise IOError(f"Failed to read file {file_path}: {str(e)}")

    @staticmethod
    def write_text(file_path: Path, content: str, create_dirs: bool = True) -> None:
        """
        Write text to file.

        Args:
            file_path: Path to file
            content: Text content to write
            create_dirs: Whether to create parent directories

        Raises:
            IOError: If file cannot be written
        """
        try:
            if create_dirs:
                file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            raise IOError(f"Failed to write file {file_path}: {str(e)}")

    @staticmethod
    def read_json(file_path: Path) -> Dict[str, Any]:
        """
        Read and parse JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            Dict: Parsed JSON data

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
            IOError: If file cannot be read
        """
        content = FileHandler.read_text(file_path)
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in file {file_path}: {str(e)}",
                e.doc,
                e.pos
            )

    @staticmethod
    def write_json(
        file_path: Path,
        data: Dict[str, Any],
        indent: int = 2,
        create_dirs: bool = True
    ) -> None:
        """
        Write data as JSON file.

        Args:
            file_path: Path to JSON file
            data: Data to write
            indent: JSON indentation level
            create_dirs: Whether to create parent directories

        Raises:
            IOError: If file cannot be written
        """
        try:
            content = json.dumps(data, indent=indent, ensure_ascii=False)
            FileHandler.write_text(file_path, content, create_dirs)
        except Exception as e:
            raise IOError(f"Failed to write JSON file {file_path}: {str(e)}")

    @staticmethod
    def load_prompt_template(template_name: str, templates_dir: Optional[Path] = None) -> str:
        """
        Load prompt template file.

        Args:
            template_name: Name of template (e.g., 'stage1_asset_identification')
            templates_dir: Optional custom templates directory

        Returns:
            str: Template content

        Raises:
            FileNotFoundError: If template doesn't exist
        """
        if templates_dir is None:
            # Default to project templates directory
            templates_dir = Path(__file__).parent.parent.parent / "templates" / "prompts"

        template_path = templates_dir / f"{template_name}.txt"
        return FileHandler.read_text(template_path)

    @staticmethod
    def load_cce_baseline(plugin_name: str, baseline_file: str = "cce_baseline.json") -> list:
        """
        Load CCE baseline for a specific plugin.

        Args:
            plugin_name: Name of plugin (e.g., 'network', 'unix')
            baseline_file: Name of baseline file

        Returns:
            list: CCE check definitions

        Raises:
            FileNotFoundError: If baseline file doesn't exist
        """
        baseline_path = (
            Path(__file__).parent.parent.parent /
            "plugins" / plugin_name / "config" / baseline_file
        )
        data = FileHandler.read_json(baseline_path)
        # Extract checks array from the JSON structure
        if isinstance(data, dict) and 'checks' in data:
            return data['checks']
        return data

    @staticmethod
    def load_device_profiles(plugin_name: str, profiles_file: str = "device_profiles.json") -> Dict:
        """
        Load device profiles for a specific plugin.

        Args:
            plugin_name: Name of plugin
            profiles_file: Name of profiles file

        Returns:
            Dict: Device profile definitions

        Raises:
            FileNotFoundError: If profiles file doesn't exist
        """
        profiles_path = (
            Path(__file__).parent.parent.parent /
            "plugins" / plugin_name / "config" / profiles_file
        )
        return FileHandler.read_json(profiles_path)

    @staticmethod
    def save_assessment_result(
        output_dir: Path,
        asset_id: str,
        result: Dict[str, Any],
        format: str = "json"
    ) -> Path:
        """
        Save assessment result to file.

        Args:
            output_dir: Output directory
            asset_id: Asset identifier (hostname, IP, etc.)
            result: Assessment result data
            format: Output format ('json' or 'both' for now)

        Returns:
            Path: Path to saved file

        Raises:
            IOError: If file cannot be written
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_asset_id = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in asset_id)
        filename = f"cce_assessment_{safe_asset_id}_{timestamp}.json"

        output_path = output_dir / filename
        FileHandler.write_json(output_path, result)

        return output_path

    @staticmethod
    def list_sample_configs(plugin_name: str) -> list:
        """
        List available sample configuration files for a plugin.

        Args:
            plugin_name: Name of plugin

        Returns:
            list: List of sample config file paths
        """
        samples_dir = (
            Path(__file__).parent.parent.parent /
            "plugins" / plugin_name / "samples"
        )

        if not samples_dir.exists():
            return []

        return list(samples_dir.glob("*.cfg")) + list(samples_dir.glob("*.txt"))

    @staticmethod
    def ensure_directory(dir_path: Path) -> None:
        """
        Ensure directory exists, create if not.

        Args:
            dir_path: Directory path to ensure
        """
        dir_path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_file_hash(file_path: Path) -> str:
        """
        Get SHA-256 hash of file content.

        Args:
            file_path: Path to file

        Returns:
            str: Hexadecimal hash string

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        import hashlib

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

        return sha256_hash.hexdigest()
