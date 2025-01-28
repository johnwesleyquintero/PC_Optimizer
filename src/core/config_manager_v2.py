import os
import platform
from pathlib import Path
import configparser
import darkdetect
import psutil
import logging

class EnvironmentConfig:
    def __init__(self, config_file='config.ini'):
        self.system = platform.system()
        self.config_dir = self._get_config_dir()
        self.config_path = self.config_dir / config_file
        self.config = self._load_config()

    def _get_config_dir(self):
        if self.system == "Windows":
            return Path(os.environ['APPDATA']) / "PC_Optimizer"
        elif self.system == "Darwin":
            return Path.home() / "Library/Application Support/PC_Optimizer"
        else:
            return Path.home() / ".config/pc_optimizer"

    def _load_config(self):
        config = configparser.ConfigParser()
        config.read_dict({
            'UI': {'theme': 'auto', 'animations': 'true'},
            'Performance': {'max_threads': 'auto'},
            'Paths': {'output_dir': 'auto'}
        })
        if self.config_path.exists():
            config.read(self.config_path)
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
        self.config_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.config_path, 'w') as configfile:
                self.config.write(configfile)
            logging.info(f"Configuration saved successfully to {self.config_path}")
        except Exception as e:
            logging.error(f"Failed to save configuration to {self.config_path}: {e}")
