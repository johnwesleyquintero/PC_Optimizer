import os
from .config_manager import EnvironmentConfig
from .logging_manager import LoggingManager


class EnvironmentManager:
    """Manages environment-specific configurations and system resources."""

    def __init__(self, config_file="config.ini"):
        """Initialize the environment manager with configuration settings.

        Args:
            config_file (str): Name of the configuration file.
        """
        self.logger = LoggingManager().get_logger(__name__)
        self.logger.info("EnvironmentManager: Initializing")
        self._config = EnvironmentConfig(config_file)
        self._validate_config()
        self._ensure_directories()
        self.logger.info(
            "EnvironmentManager: Environment manager initialized successfully"
        )

    def _validate_config(self):
        """Validate configuration values and set defaults if missing."""
        # Define acceptable ranges and default values
        config_ranges = {
            "max_threads": {"min": 1, "max": 32, "default": 4},
            "log_level": {
                "values": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                "default": "INFO",
            },
            "theme": {
                "required_keys": ["base", "text", "primary"],
                "default": {
                    "base": "#F0F0F0",
                    "text": "#000000",
                    "primary": "#007ACC",
                },
            },
        }

        # Validate and fix configuration values
        try:
            # Validate max_threads
            if not hasattr(self._config, "max_threads"):
                self.logger.warning("max_threads not found in config, using default")
                self._config.max_threads = config_ranges["max_threads"]["default"]
            else:
                max_threads = self._config.max_threads
                min_threads = config_ranges["max_threads"]["min"]
                max_allowed = config_ranges["max_threads"]["max"]
                if not isinstance(max_threads, int) or not (
                    min_threads <= max_threads <= max_allowed
                ):
                    msg = f"Invalid max_threads value: {max_threads}, using default"
                    self.logger.warning(msg)
                    self._config.max_threads = config_ranges["max_threads"]["default"]

            # Validate log_level
            if (
                not hasattr(self._config, "log_level")
                or self._config.log_level not in config_ranges["log_level"]["values"]
            ):
                msg = "Invalid or missing log_level in config, using default"
                self.logger.warning(msg)
                self._config.log_level = config_ranges["log_level"]["default"]

            # Validate theme
            if not hasattr(self._config, "theme") or not isinstance(
                self._config.theme, dict
            ):
                msg = "Theme configuration missing or invalid, using default"
                self.logger.warning(msg)
                self._config.theme = config_ranges["theme"]["default"].copy()
            else:
                missing_keys = [
                    key
                    for key in config_ranges["theme"]["required_keys"]
                    if key not in self._config.theme
                ]
                if missing_keys:
                    msg = f"Missing theme keys: {missing_keys}, using defaults for those keys"
                    self.logger.warning(msg)
                    for key in missing_keys:
                        self._config.theme[key] = config_ranges["theme"]["default"][key]

            # Save validated configuration
            self._config.save_config()
            self.logger.info("Configuration validation completed successfully")

        except Exception as e:
            msg = f"Configuration validation failed: {e}"
            self.logger.error(msg)
            raise

    def initialize(self) -> bool:
        """Initialize the environment manager.

        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            self._ensure_directories()
            return True
        except Exception as e:
            msg = f"Failed to initialize environment: {e}"
            self.logger.error(msg)
            return False

    def _ensure_directories(self):
        """Ensure all required directories exist.

        Creates the following directories if they don't exist:
        - Output directory for logs and data
        - Cache directory for temporary data
        - Config directory for settings
        - Backup directory for system backups
        - Temp directory for processing
        """
        try:
            required_dirs = [
                self._config.output_dir,  # Main output directory
                self._config.output_dir / "cache",  # Cache directory
                self._config.output_dir / "config",  # Configuration directory
                self._config.output_dir / "backups",  # Backup directory
                self._config.output_dir / "temp",  # Temporary processing directory
            ]

            for directory in required_dirs:
                try:
                    directory.mkdir(parents=True, exist_ok=True)
                    # Verify directory permissions
                    if not os.access(directory, os.W_OK):
                        msg = f"Directory {directory} exists but is not writable"
                        self.logger.warning(msg)
                except PermissionError as pe:
                    msg = f"Permission denied creating directory {directory}: {pe}"
                    self.logger.error(msg)
                    raise
                except Exception as e:
                    msg = f"Failed to create directory {directory}: {e}"
                    self.logger.error(msg)
                    raise

            self.logger.info("All required directories created successfully")
        except Exception as e:
            msg = f"EnvironmentManager: Failed to create required directories: {e}"
            self.logger.error(msg)
            raise

    @property
    def system(self):
        """Get the current operating system."""
        return self._config.system

    @property
    def theme(self):
        """Get the current UI theme."""
        return self._config.theme

    @property
    def max_threads(self):
        """Get the maximum number of threads to use."""
        return self._config.max_threads

    @property
    def output_dir(self):
        """Get the output directory path."""
        return self._config.output_dir

    def save_config(self):
        """Save the current configuration to file."""
        try:
            self._config.save_config()
            self.logger.info("EnvironmentManager: Configuration saved successfully")
        except Exception as e:
            msg = f"EnvironmentManager: Failed to save configuration: {e}"
            self.logger.error(msg)
            raise

    def cleanup(self):
        """Cleanup resources and save configuration before shutdown."""
        try:
            self.save_config()
            self.logger.info("EnvironmentManager: Cleanup completed successfully")
        except Exception as e:
            msg = f"EnvironmentManager: Cleanup failed: {e}"
            self.logger.error(msg)
            raise
