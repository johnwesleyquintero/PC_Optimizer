import argparse
from src.core.environment_manager import EnvironmentConfig
from src.core.performance_optimizer import TaskOptimizer
from src.core.cli_manager import AdaptiveCLI
import sys

if __name__ == "__main__":
    cli = AdaptiveCLI()
    cli.run()
