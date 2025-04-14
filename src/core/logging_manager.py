import logging
import configparser
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


class LoggingManager:
    """
    Centralized logging management for the PC Optimizer application.

    This class implements a singleton pattern to ensure only one instance
    of the logger is used throughout the application. It configures
    both file and console logging based on settings in the configuration file.
    """

    _instance = None

    def __new__(cls, config_path: Optional[str] = None):
        if cls._instance is None:
            cls._instance = super(LoggingManager, cls).__new__(cls)
            cls._instance._setup_basic_logging()
        return cls._instance

    def __init__(self, config_path: Optional[str] = None):
        if not hasattr(self, "initialized"):
            self.config = configparser.ConfigParser()
            if config_path:
                self.config.read(config_path)
            self.log_dir = Path(self.config.get("Logging", "log_dir", fallback="logs"))
            self.log_dir.mkdir(parents=True, exist_ok=True)
            self._setup_enhanced_logging()
            self.initialized = True
            self.logger = self.get_logger(__name__)

    def _setup_basic_logging(self):
        """Set up basic logging configuration for initial startup."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    def _setup_enhanced_logging(self):
        """Configure the logging system with file and console handlers based on config."""
        # Get configuration values
        log_level = getattr(
            logging, self.config.get("Logging", "log_level", fallback="INFO").upper()
        )
        log_format = self.config.get(
            "Logging",
            "log_format",
            fallback="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        max_file_size = self.config.getint(
            "Logging", "max_file_size", fallback=10485760
        )  # 10MB
        backup_count = self.config.getint("Logging", "backup_count", fallback=5)

        # Create formatter
        formatter = logging.Formatter(log_format)

        # Root logger configuration
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # File handler (if enabled)
        if self.config.getboolean("Logging", "file_logging", fallback=True):
            log_file = self.log_dir / self.config.get(
                "Logging", "log_file", fallback="SentinelPC.log"
            )
            file_handler = RotatingFileHandler(
                log_file, maxBytes=max_file_size, backupCount=backup_count
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

        # Console handler (if enabled)
        if self.config.getboolean("Logging", "console_logging", fallback=True):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            console_handler.setFormatter(formatter)
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
