import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

class LoggingManager:
    """Centralized logging management for the PC Optimizer application."""

    def __init__(self, log_dir: Optional[Path] = None):
        self.log_dir = log_dir or Path('logs')
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._setup_logging()

    def _setup_logging(self):
        """Configure the logging system with file and console handlers."""
        # Generate log filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = self.log_dir / f'pc_optimizer_{timestamp}.log'

        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )

        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)

        # Root logger configuration
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger with the specified name.

        Args:
            name (str): Name for the logger

        Returns:
            logging.Logger: Configured logger instance
        """
        return logging.getLogger(name)

    def set_level(self, level: int):
        """Set the logging level for all handlers.

        Args:
            level (int): Logging level (e.g., logging.DEBUG, logging.INFO)
        """
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        for handler in root_logger.handlers:
            handler.setLevel(level)