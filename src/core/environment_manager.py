import os
import platform
from pathlib import Path
import configparser
import darkdetect
import psutil
from .logging_manager import LoggingManager

# Constants
DARK_THEME = 'dark'
LIGHT_THEME = 'light'
WINDOWS_SYSTEM = 'Windows'
MEMORY_THRESHOLD_2GB = 2 * 1024**3

class EnvironmentConfig:
    def __init__(self, config_file='config.ini'):
        self.logger = LoggingManager().get_logger(__name__)
        self.logger.info("EnvironmentConfig: Initializing configuration")
        self.system = platform.system()
        self.config_dir = self._get_config_dir()
        self.logger.info(f"EnvironmentConfig: Config directory is {self.config_dir}")
        self.config_path = self.config_dir / config_file
        self.config = self._load_config()
        self.logger.info(f"EnvironmentConfig: Configuration loaded from {self.config_path}")

    def _get_config_dir(self):
        if self.system == "Windows":
            return Path(os.environ['APPDATA']) / "PC_Optimizer"
        elif self.system == "Darwin":
            return Path.home() / "Library/Application Support/PC_Optimizer"
        else:
            return Path.home() / ".config/pc_optimizer"

    def _load_config(self):
        self.logger.info("EnvironmentConfig: Loading configuration")
        config = configparser.ConfigParser()
        config.read_dict({
            'UI': {'theme': 'auto', 'animations': 'true'},
            'Performance': {'max_threads': 'auto'},
            'Paths': {'output_dir': 'auto'}
        })
        if self.config_path.exists():
            config.read(self.config_path)
        self.logger.info("EnvironmentConfig: Configuration loading completed")
        return config

    @property
    def theme(self):
        theme_choice = self.config['UI']['theme']
        if theme_choice == 'auto':
            return 'dark' if darkdetect.isDark() else 'light'
        return theme_choice

    @property
    def max_threads(self):
        if self.config['Performance']['max_threads'] == 'auto':
            return psutil.cpu_count(logical=False)
        return int(self.config['Performance']['max_threads'])

    @property
    def output_dir(self):
        if self.config['Paths']['output_dir'] == 'auto':
            return self._default_output_dir()
        return Path(self.config['Paths']['output_dir'])

    def _default_output_dir(self):
        if self.system == "Windows":
            return Path(os.environ['USERPROFILE']) / "Documents/PC_Optimizer"
        return Path.home() / "PC_Optimizer"

    def save_config(self):
        self.logger.info("EnvironmentConfig: Saving configuration")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.config_path, 'w') as configfile:
                self.config.write(configfile)
            self.logger.info(f"Configuration saved successfully to {self.config_path}")
        except Exception as e:
            self.logger.error(f"Failed to save configuration to {self.config_path}: {e}")

class EnvironmentManager:
    """Manages environment-specific configurations and system resources for the PC Optimizer application."""

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
            logging.info("EnvironmentManager: Configuration saved successfully")
        except Exception as e:
            logging.error(f"EnvironmentManager: Failed to save configuration: {e}")
            raise
