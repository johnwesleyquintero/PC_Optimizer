"""SentinelPC CLI Interface

This module provides the command-line interface for SentinelPC.
"""

import sys
import argparse
from typing import Optional
from ..core.sentinel_core import SentinelCore


class SentinelCLI:
    """Command-line interface for SentinelPC."""

    def __init__(self, core: SentinelCore):
        """Initialize CLI interface.

        Args:
            core: Initialized SentinelCore instance
        """
        self.core = core

    def display_system_info(self) -> None:
        """Display current system information."""
        info = self.core.get_system_info()
        if "error" in info:
            print(f"Error getting system info: {info['error']}")
            return

        print("\nSystem Information:")
        print("-" * 20)
        for key, value in info.items():
            print(f"{key}: {value}")

    def display_optimization_results(self, results: dict) -> None:
        """Display optimization results.

        Args:
            results: Dictionary containing optimization results
        """
        if not results["success"]:
            print(f"\nOptimization failed: {results.get('error', 'Unknown error')}")
            return

        print("\nOptimization Results:")
        print("-" * 20)
        print("Initial State:")
        for key, value in results["initial_state"].items():
            print(f"  {key}: {value}")

        print("\nOptimizations Performed:")
        for opt in results["optimizations"]:
            print(f"  - {opt}")

        print("\nFinal State:")
        for key, value in results["final_state"].items():
            print(f"  {key}: {value}")

    def run(self, profile: Optional[str] = None) -> None:
        """Run the CLI interface.

        Args:
            profile: Optional optimization profile to use
        """
        print(f"SentinelPC CLI v{self.core.version}\n")

        # Display initial system info
        self.display_system_info()

        # Run optimization
        print("\nRunning optimization...")
        results = self.core.run_optimization(profile)

        # Display results
        self.display_optimization_results(results)
