from .config_manager import EnvironmentConfig

class EnvironmentManager:
    """Manages environment-specific configurations and system resources for the SentinelPC application."""

    def __init__(self, config_file='config.ini'):
        """Initialize the environment manager with configuration settings.

        Args:
            config_file (str): Name of the configuration file.
        """
        self.logger = LoggingManager().get_logger(__name__)
        self.logger.info("EnvironmentManager: Initializing environment manager")
        self._config = EnvironmentConfig(config_file)
        self._ensure_directories()
        self.logger.info("EnvironmentManager: Environment manager initialized successfully")

    def initialize(self) -> bool:
        """Initialize the environment manager.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            self._ensure_directories()
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize environment: {e}")
            return False

    def _ensure_directories(self):
        """Ensure all required directories exist."""
        try:
            output_dir = self._config.output_dir
            output_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"EnvironmentManager: Created output directory at {output_dir}")
        except Exception as e:
            self.logger.error(f"EnvironmentManager: Failed to create output directory: {e}")
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
            self.logger.error(f"EnvironmentManager: Failed to save configuration: {e}")
            raise

    def cleanup(self):
        """Cleanup resources and save configuration before shutdown."""
        try:
            self.save_config()
            self.logger.info("EnvironmentManager: Cleanup completed successfully")
        except Exception as e:
            self.logger.error(f"EnvironmentManager: Cleanup failed: {e}")
            raise
