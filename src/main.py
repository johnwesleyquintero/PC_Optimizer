"""SentinelPC Main Entry Point

This script serves as the unified entry point for SentinelPC,
handling both CLI and GUI modes.
"""

import sys
import argparse
from typing import Optional
from .core.sentinel_core import SentinelCore
from .core.logging_manager import LoggingManager

def parse_args() -> argparse.Namespace:
    """Parse command line arguments.
    
    Returns:
        Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="SentinelPC - Advanced PC Optimization Tool"
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run in CLI mode (default is GUI mode)"
    )
    parser.add_argument(
        "--profile",
        type=str,
        help="Optimization profile to use"
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information"
    )
    return parser.parse_args()

def run_cli_mode(core: SentinelCore, profile: Optional[str] = None) -> None:
    """Run SentinelPC in CLI mode.
    
    Args:
        core: Initialized SentinelCore instance
        profile: Optional optimization profile to use
    """
    from .cli.sentinel_cli import SentinelCLI
    cli = SentinelCLI(core)
    cli.run(profile)

def run_gui_mode(core: SentinelCore) -> None:
    """Run SentinelPC in GUI mode.
    
    Args:
        core: Initialized SentinelCore instance
    """
    from .gui.sentinel_gui import SentinelGUI
    gui = SentinelGUI(core)
    gui.run()

def main() -> None:
    """Main entry point for SentinelPC."""
    # Initialize logging
    logger = LoggingManager().get_logger(__name__)
    
    try:
        # Parse command line arguments
        args = parse_args()
        
        # Show version if requested
        if args.version:
            core = SentinelCore()
            print(f"SentinelPC v{core.version}")
            sys.exit(0)
        
        # Initialize core
        core = SentinelCore()
        if not core.initialize():
            logger.error("Failed to initialize SentinelPC Core")
            sys.exit(1)
        
        # Run in appropriate mode
        try:
            if args.cli:
                run_cli_mode(core, args.profile)
            else:
                run_gui_mode(core)
        finally:
            core.shutdown()
            
    except Exception as e:
        logger.error("Fatal error: %s", str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()