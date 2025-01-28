import argparse
from src.core.environment_manager import EnvironmentConfig

class AdaptiveCLI:
    def __init__(self):
        self.config = EnvironmentConfig()
        self.parser = argparse.ArgumentParser(
            description='SellSmart Environment-Adaptive Optimizer',
            epilog=self._get_environment_footer()
        )

    def _get_environment_footer(self):
        return f"""\nCurrent Environment:
  - OS: {self.config.system}
  - Theme: {self.config.theme.capitalize()}
  - Threads: {self.config.max_threads}
  - Output Directory: {self.config.output_dir}"""
