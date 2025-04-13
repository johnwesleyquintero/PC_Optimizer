"""SentinelPC Main Entry Point

This module serves as the main entry point for the SentinelPC application.
It initializes core components, sets up the GUI, and handles application lifecycle.
"""

import sys
import logging
import platform
import tkinter as tk
# Conditional import for Windows DPI awareness
try:
    from ctypes import windll
except ImportError:
    windll = None # Not on Windows or ctypes not available

from src.core.sentinel_core import SentinelCore
from src.gui.sentinel_gui import SentinelGUI

# --- Logging Configuration ---
def setup_logging():
    """Configures basic logging for the application."""
    logging.basicConfig(
        level=logging.INFO, # Set to logging.DEBUG for more verbose output
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout), # Log to console
            # Optionally add a FileHandler here:
            # logging.FileHandler("sentinelpc.log")
        ]
    )
    logging.info("Logging configured.")

# --- Platform Specific Enhancements ---
def set_dpi_awareness():
    """Sets DPI awareness on Windows for better scaling."""
    if platform.system() == "Windows" and windll:
        try:
            # Query DPI Awareness (Windows 10 and later)
            # awareness = windll.shcore.GetProcessDpiAwareness(0)
            # Set DPI Awareness (requires Windows 8.1 or later)
            # PROCESS_PER_MONITOR_DPI_AWARE = 2
            windll.shcore.SetProcessDpiAwareness(2)
            logging.info("Process DPI awareness set to Per Monitor DPI Aware.")
        except AttributeError:
            # Fallback for older Windows versions (Vista and later)
            try:
                windll.user32.SetProcessDPIAware()
                logging.info("Process DPI awareness set using SetProcessDPIAware().")
            except AttributeError:
                logging.warning("Could not set DPI awareness. GUI scaling might be suboptimal on high-DPI displays.")
        except Exception as e:
            logging.error(f"Error setting DPI awareness: {e}")

# --- Main Application Logic ---
def main():
    """Main entry point for SentinelPC application."""
    setup_logging()
    set_dpi_awareness()

    logging.info("Starting SentinelPC application...")
    core = None
    gui = None

    try:
        # Initialize core components
        logging.info("Initializing SentinelCore...")
        core = SentinelCore()
        logging.info(f"SentinelCore initialized (Version: {core.version}).")

        # Create GUI
        logging.info("Initializing SentinelGUI...")
        gui = SentinelGUI(core)
        logging.info("SentinelGUI initialized.")

        # Run the GUI main loop
        logging.info("Starting GUI main loop...")
        gui.run() # gui.run() now contains the mainloop call and worker cleanup

    except Exception as e:
        logging.exception("An unhandled exception occurred during application startup or execution.")
        # Optionally show a simple error dialog if tkinter is partially available
        try:
            import tkinter.messagebox
            tkinter.messagebox.showerror("Fatal Error", f"An unexpected error occurred:\n{e}\nPlease check the logs for details.")
        except Exception:
            pass # If tkinter itself failed, just rely on console/log output
        sys.exit(1) # Exit with error code

    finally:
        # Ensure resources are cleaned up, although gui.run() should handle the worker
        logging.info("SentinelPC application shutting down.")
        # The worker stop is now handled within gui.run()'s finally block,
        # but adding a log message here confirms shutdown sequence.

if __name__ == "__main__":
    main()
