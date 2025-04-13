import logging
from pathlib import Path
from .config_manager import EnvironmentConfig as BaseEnvironmentConfig

class EnvironmentManager:
    """Manages environment-specific configurations and system resources for the PC Optimizer application."""

    def __init__(self, config_file='config.ini'):
        """Initialize the environment manager with configuration settings.

        Args:
            config_file (str): Name of the configuration file.
        """
        logging.info("EnvironmentManager: Initializing environment manager")
        self._config = BaseEnvironmentConfig(config_file)
        self._ensure_directories()
        logging.info("EnvironmentManager: Environment manager initialized successfully")

    def _ensure_directories(self):
        """Ensure all required directories exist."""
        try:
            output_dir = self._config.output_dir
            output_dir.mkdir(parents=True, exist_ok=True)
            logging.info(f"EnvironmentManager: Created output directory at {output_dir}")
        except Exception as e:
            logging.error(f"EnvironmentManager: Failed to create output directory: {e}")
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
            logging.info("EnvironmentManager: Configuration saved successfully")
        except Exception as e:
            logging.error(f"EnvironmentManager: Failed to save configuration: {e}")
            raise
