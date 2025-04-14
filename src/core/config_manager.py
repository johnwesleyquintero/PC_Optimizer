"""Configuration Manager for SentinelPC

This module handles loading, saving, and managing configuration settings.
"""

import os
import platform
import logging
from pathlib import Path
import configparser
import darkdetect
import psutil
from .logging_manager import LoggingManager

# Constants
DARK_THEME = "dark"
LIGHT_THEME = "light"
WINDOWS_SYSTEM = "Windows"
MEMORY_THRESHOLD_2GB = 2 * 1024**3


class ConfigManager:
    """Manages configuration settings for SentinelPC.

    This class handles loading, saving, and updating configuration settings
    from a configuration file.
    """

    def __init__(self, config_file="config.ini"):
        """Initialize ConfigManager.

        Args:
            config_file: Name of the configuration file
        """
        self.logger = LoggingManager().get_logger(__name__)
        self.logger.info("ConfigManager: Initializing configuration")
        self.system = platform.system()
        self.config_dir = self._get_config_dir()
        self.logger.info(f"ConfigManager: Config directory is {self.config_dir}")
        self.config_path = self.config_dir / config_file
        self.config = self._load_config()
        self.logger.info(f"ConfigManager: Configuration loaded from {self.config_path}")

    def _get_config_dir(self) -> Path:
        """Get the configuration directory path.

        Returns:
            Path to configuration directory
        """
        if self.system == "Windows":
            return Path(os.environ["APPDATA"]) / "SentinelPC"
        elif self.system == "Darwin":
            return Path.home() / "Library/Application Support/SentinelPC"
        else:
            return Path.home() / ".config/sentinelpc"

    def _load_config(self) -> configparser.ConfigParser:
        """Load configuration from file.

        Returns:
            Loaded configuration
        """
        self.logger.info("ConfigManager: Loading configuration")
        config = configparser.ConfigParser()
        config.read_dict(
            {
                "UI": {"theme": "auto", "animations": "true"},
                "Performance": {"max_threads": "auto"},
                "Paths": {"output_dir": "auto"},
                "Profiles": {"default": "balanced"},
            }
        )
        if self.config_path.exists():
            config.read(self.config_path)
        self.logger.info("ConfigManager: Configuration loading completed")
        return config

    def get_theme(self) -> str:
        """Get current theme setting.

        Returns:
            Current theme ('dark' or 'light')
        """
        theme_choice = self.config["UI"]["theme"]
        if theme_choice == "auto":
            return DARK_THEME if darkdetect.isDark() else LIGHT_THEME
        return theme_choice

    def get_max_threads(self) -> int:
        """Get maximum number of threads to use.

        Returns:
            Maximum number of threads
        """
        if self.config["Performance"]["max_threads"] == "auto":
            return psutil.cpu_count(logical=False)
        return int(self.config["Performance"]["max_threads"])

    def get_output_dir(self) -> Path:
        """Get output directory path.

        Returns:
            Path to output directory
        """
        if self.config["Paths"]["output_dir"] == "auto":
            return self._default_output_dir()
        return Path(self.config["Paths"]["output_dir"])

    def load_config(self) -> bool:
        """Load configuration from file.

        Returns:
            True if configuration was loaded successfully, False otherwise
        """
        try:
            self.config = self._load_config()
            return True
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            return False

    def get_default_profile(self) -> str:
        """Get default optimization profile.

        Returns:
            Name of default profile
        """
        return self.config["Profiles"]["default"]

    def _default_output_dir(self) -> Path:
        """Get default output directory path.

        Returns:
            Path to default output directory
        """
        if self.system == "Windows":
            return Path(os.environ["USERPROFILE"]) / "Documents/SentinelPC"
        return Path.home() / "SentinelPC"

    def save_config(self) -> None:
        """Save current configuration to file."""
        self.logger.info("ConfigManager: Saving configuration")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.config_path, "w") as configfile:
                self.config.write(configfile)
            self.logger.info(f"Configuration saved successfully to {self.config_path}")
        except Exception as e:
            self.logger.error(
                f"Failed to save configuration to {self.config_path}: {e}"
            )

    def update_config(self, updates: dict) -> None:
        """Update configuration with new values.

        Args:
            updates: Dictionary of configuration updates
        """
        for section, values in updates.items():
            if section not in self.config:
                self.config[section] = {}
            for key, value in values.items():
                self.config[section][key] = str(value)
        self.save_config()


class EnvironmentConfig:
    """
    Provides environment-specific configuration settings.
    """

    def __init__(self, config_file="config.ini"):
        self.system = platform.system()
        self.config_dir = self._get_config_dir()
        self.config_path = self.config_dir / config_file
        self.config = self._load_config()
        self.logger = LoggingManager().get_logger(__name__)
        self.logger.info(
            f"EnvironmentConfig: Configuration loaded from {self.config_path}"
        )

    def _get_config_dir(self) -> Path:
        """
        Determines the appropriate configuration directory based on the operating system.

        Returns:
            Path: The path to the configuration directory.
        """
        if self.system == "Windows":
            return Path(os.environ["APPDATA"]) / "SentinelPC"
        elif self.system == "Darwin":
            return Path.home() / "Library/Application Support/SentinelPC"
        else:
            return Path.home() / ".config/SentinelPC"

    def _load_config(self) -> configparser.ConfigParser:
        """
        Loads the configuration settings from the configuration file.

        Returns:
            configparser.ConfigParser: The loaded configuration settings.
        """
        self.logger.info("EnvironmentConfig: Loading configuration")
        config = configparser.ConfigParser()
        config.read_dict(
            {
                "UI": {"theme": "auto", "animations": "true"},
                "Performance": {"max_threads": "auto"},
                "Paths": {"output_dir": "auto"},
            }
        )
        if self.config_path.exists():
            config.read(self.config_path)
        self.logger.info("EnvironmentConfig: Configuration loading completed")
        return config

    @property
    def theme(self):
        theme_choice = self.config["UI"]["theme"]
        if theme_choice == "auto":
            return "dark" if darkdetect.isDark() else "light"
        return theme_choice

    @property
    def max_threads(self):
        if self.config["Performance"]["max_threads"] == "auto":
            return psutil.cpu_count(logical=False)
        return int(self.config["Performance"]["max_threads"])

    @property
    def output_dir(self):
        if self.config["Paths"]["output_dir"] == "auto":
            return self._default_output_dir()
        return Path(self.config["Paths"]["output_dir"])

    def _default_output_dir(self) -> Path:
        """
        Gets the default output directory based on the operating system.

        Returns:
            Path: The default output directory.
        """
        if self.system == "Windows":
            return Path(os.environ["USERPROFILE"]) / "Documents/SentinelPC"
        return Path.home() / "SentinelPC"

    def save_config(self) -> None:
        """
        Saves the current configuration settings to the configuration file.
        """
        logging.info("EnvironmentConfig: Saving configuration")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.config_path, "w") as configfile:
                self.config.write(configfile)
            logging.info(f"Configuration saved successfully to {self.config_path}")
        except Exception as e:
            logging.error(f"Failed to save configuration to {self.config_path}: {e}")
