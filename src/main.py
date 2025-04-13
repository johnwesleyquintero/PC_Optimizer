"""SentinelPC Main Entry Point

This module serves as the main entry point for the SentinelPC application.
"""

import sys
import tkinter as tk
from src.core.sentinel_core import SentinelCore
from src.gui.sentinel_gui import SentinelGUI

def main():
    """Main entry point for SentinelPC application."""
    try:
        # Initialize core components
        core = SentinelCore()
        
        # Create and run GUI
        gui = SentinelGUI(core)
        gui.root.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()