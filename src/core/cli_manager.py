import argparse
from src.core.environment_manager import EnvironmentConfig


class AdaptiveCLI:
    """
    AdaptiveCLI class for creating a command-line interface.
    """

    def __init__(self):
        """Initializes the AdaptiveCLI.

        Sets up environment configuration and argument parser.
        """
        self.config = EnvironmentConfig()
        self.parser = argparse.ArgumentParser(
            description="SellSmart Environment-Adaptive Optimizer",
            epilog=self._get_environment_footer(),
        )

    def _get_environment_footer(self):
        """
        Formats and returns the current environment information as a string.

        Returns:
            str: Formatted environment information.
        """
        return f"""\nCurrent Environment:
  - OS: {self.config.system}
  - Theme: {self.config.theme.capitalize()}
  - Threads: {self.config.max_threads}
  - Output Directory: {self.config.output_dir}"""
