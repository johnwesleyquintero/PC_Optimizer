import argparse
import sys
from ..core.environment_manager import EnvironmentConfig
from ..core.performance_optimizer import TaskOptimizer
from ..core.cli_manager import AdaptiveCLI

if __name__ == "__main__":
    cli = AdaptiveCLI()
    cli.run()
