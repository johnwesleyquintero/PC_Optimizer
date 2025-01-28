# PC Optimizer

A comprehensive Python application designed to optimize your PC's performance. This tool offers both a Command-Line Interface (CLI) and a Graphical User Interface (GUI) for enhanced usability and flexibility.

## Revamped Project Structure

The project is now organized as follows:

```
PC_Optimizer/
├── main.py               # Main application entry point
├── src/
│   ├── cli/              # CLI-related components
│   │   └── pc_optimizer_cli_v2.py   # CLI implementation
│   ├── gui/              # GUI-related components
│   │   └── pc_optimizer_gui_v2.py   # GUI implementation
│   └── core/             # Core functionality
│       ├── cli_manager.py          # CLI logic
│       ├── environment_manager.py  # Environment configuration
│       └── performance_optimizer.py# Performance optimization tasks
├── config/               # Configuration files
├── docs/                 # Documentation
│   └── README.md         # Main documentation
├── scripts/              # Build/deployment scripts
├── spec/                 # PyInstaller spec files
├── build/                # Build artifacts (auto-generated)
└── dist/                 # Distribution outputs
```

## Features

**Environment-Aware Features:**

*   **Adaptive Configuration:** Automatically adjusts settings based on the detected operating system (Windows, macOS, Linux).
*   **Theme Detection:** Auto-detects and applies dark or light theme based on system preferences.
*   **Performance Scaling:** Dynamically optimizes performance parameters like thread count based on available system resources.
*   **Cross-Platform Paths:** Uses platform-appropriate file paths for configuration and output directories.
*   **Dynamic UI Scaling:** Adjusts UI elements for different display resolutions (Windows).

**Existing Features (Both CLI and GUI versions):**

*   **Clean Temporary Files:** Removes temporary files and folders from common locations.
*   **Check Disk Usage:** Displays disk usage statistics for all partitions.

**GUI version only:**

*   **Manage Startup Programs (Windows only):** Lists startup programs (implementation in progress).
*   **Optimize Power Settings (Windows only):** Optimizes power settings (implementation in progress).
*   **Run Disk Cleanup (Windows only):** Runs the built-in Windows disk cleanup utility (implementation in progress).

## Requirements

*   Python 3.x
*   psutil (install using `pip install psutil`)
*   (For GUI) Tkinter (usually included with Python)

## Usage

### Command-Line Interface (CLI)

1. Open a terminal as administrator (recommended, especially on Windows).
2. Navigate to the `PC_Optimizer` directory.
3. Run the CLI using `python main.py`.
4. The CLI will provide information about the current environment.

### Graphical User Interface (GUI)

1. Navigate to the `PC_Optimizer` directory.
2. Run the GUI using `python src/gui/pc_optimizer_gui_v2.py`.
3. Select the optimizations you want to perform using the checkboxes.
4. Click "Run Selected Optimizations".
5. A log of the operations will be displayed in the log area.

## Creating an Executable (GUI)

1. Install PyInstaller: `pip install pyinstaller`
2. Navigate to the `PC_Optimizer` directory.
3. Create a spec file or use this command: `pyinstaller --onefile --windowed --name PCOptimizerGUI src/gui/pc_optimizer_gui_v2.py`
4. The executable will be in the `dist` folder.

## Additional Notes

*   This script performs basic optimizations only. For more advanced optimizations, consider manual bloatware removal, driver updates, hardware upgrades, proper antivirus scans, SSD optimization (if applicable), and registry cleaning (for advanced users only).
*   The script focuses on safe operations, but system modifications always carry some risk. Back up important data before running the script.
*   Some features are Windows-specific.
*   The GUI version provides a dark theme, real-time logging, and automatic disabling of OS-specific options.
*   Future improvements may include a progress bar, more error handling, visual styling customization, save/load configurations, and undo functionality.
