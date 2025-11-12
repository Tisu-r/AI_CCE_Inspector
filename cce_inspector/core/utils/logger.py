"""
Logging utility for CCE Inspector.

Provides structured logging with file and console output.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class CCELogger:
    """
    Custom logger for CCE Inspector with structured output.
    """

    _instance: Optional['CCELogger'] = None

    def __new__(cls, *args, **kwargs):
        """Singleton pattern to ensure single logger instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        name: str = "cce_inspector",
        level: str = "INFO",
        log_file: Optional[Path] = None,
        log_to_console: bool = True
    ):
        """
        Initialize logger.

        Args:
            name: Logger name
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional file path for log output
            log_to_console: Whether to output to console
        """
        # Prevent re-initialization
        if hasattr(self, '_initialized'):
            return

        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        self.logger.handlers.clear()  # Clear any existing handlers

        # Create formatters
        self.detailed_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        self.simple_formatter = logging.Formatter(
            fmt='%(levelname)-8s | %(message)s'
        )

        # Console handler
        if log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, level.upper()))
            console_handler.setFormatter(self.simple_formatter)
            self.logger.addHandler(console_handler)

        # File handler
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)  # Always log everything to file
            file_handler.setFormatter(self.detailed_formatter)
            self.logger.addHandler(file_handler)

        self._initialized = True

    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(message, extra=kwargs)

    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, **kwargs):
        """Log error message."""
        self.logger.error(message, extra=kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self.logger.critical(message, extra=kwargs)

    def exception(self, message: str, **kwargs):
        """Log exception with traceback."""
        self.logger.exception(message, extra=kwargs)

    def stage_start(self, stage_name: str, stage_number: int):
        """Log start of assessment stage."""
        separator = "=" * 60
        self.logger.info(f"\n{separator}")
        self.logger.info(f"Stage {stage_number}: {stage_name}")
        self.logger.info(f"{separator}")

    def stage_complete(self, stage_name: str, duration: float):
        """Log completion of assessment stage."""
        self.logger.info(f"✓ {stage_name} completed in {duration:.2f} seconds")

    def check_result(self, check_id: str, status: str, message: str = ""):
        """
        Log individual check result.

        Args:
            check_id: CCE check identifier
            status: Result status (pass, fail, manual_review)
            message: Optional additional message
        """
        status_symbols = {
            "pass": "✓",
            "fail": "✗",
            "manual_review": "?"
        }
        symbol = status_symbols.get(status, "•")
        msg = f"{symbol} {check_id}: {status.upper()}"
        if message:
            msg += f" - {message}"

        if status == "fail":
            self.logger.warning(msg)
        elif status == "pass":
            self.logger.info(msg)
        else:
            self.logger.info(msg)

    def summary(self, total: int, passed: int, failed: int, manual: int):
        """
        Log assessment summary.

        Args:
            total: Total checks performed
            passed: Number of passed checks
            failed: Number of failed checks
            manual: Number of checks requiring manual review
        """
        separator = "=" * 60
        self.logger.info(f"\n{separator}")
        self.logger.info("ASSESSMENT SUMMARY")
        self.logger.info(f"{separator}")
        self.logger.info(f"Total Checks:     {total}")
        self.logger.info(f"Passed:           {passed} ({passed/total*100:.1f}%)")
        self.logger.info(f"Failed:           {failed} ({failed/total*100:.1f}%)")
        self.logger.info(f"Manual Review:    {manual} ({manual/total*100:.1f}%)")
        self.logger.info(f"{separator}\n")


# Global logger instance
_logger: Optional[CCELogger] = None


def get_logger(
    name: str = "cce_inspector",
    level: str = "INFO",
    log_file: Optional[Path] = None,
    log_to_console: bool = True
) -> CCELogger:
    """
    Get or create the global logger instance.

    Args:
        name: Logger name
        level: Logging level
        log_file: Optional log file path
        log_to_console: Whether to output to console

    Returns:
        CCELogger: Global logger instance
    """
    global _logger
    if _logger is None:
        _logger = CCELogger(name, level, log_file, log_to_console)
    return _logger


def configure_logger_from_config(config) -> CCELogger:
    """
    Configure logger from CCEConfig instance.

    Args:
        config: CCEConfig instance

    Returns:
        CCELogger: Configured logger instance
    """
    return get_logger(
        level=config.log_level,
        log_file=config.log_file,
        log_to_console=True
    )
