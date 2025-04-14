<p align="center">
  <img src="_wwwroot/Assets/Branding/logo.svg" alt="Sentinel PC Logo" width="400">
</p>

<h1 align="center">SentinelPC: Your Ultimate Workspace Guardian 🛡️</h1>

<p align="center">
  <em>A comprehensive solution for optimizing PC performance, managing configurations, and improving the overall user experience through a unified CLI and GUI.</em>
</p>

<p align="center">
  <!-- Add relevant badges here once CI is stable, e.g., Build Status, Latest Release -->
  <!-- Example: <a href="https://github.com/johnwesleyquintero/SentinelPC/actions/workflows/main.yml"><img src="https://github.com/johnwesleyquintero/SentinelPC/actions/workflows/main.yml/badge.svg" alt="Build Status"></a> -->
  <a href="https://github.com/johnwesleyquintero/SentinelPC/releases/latest"><img src="https://img.shields.io/github/v/release/johnwesleyquintero/SentinelPC?include_prereleases&label=latest%20release&color=blue" alt="Latest Release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/johnwesleyquintero/SentinelPC" alt="License"></a>
</p>

---

## Overview

SentinelPC aims to be your go-to tool for keeping your Windows PC running smoothly. It combines various optimization techniques, configuration management, and system monitoring into a single application accessible via both a command-line interface (CLI) and a graphical user interface (GUI).

## ✨ Features

*   **Unified Interface:** Access all features through a user-friendly GUI or a powerful CLI.
*   **Performance Optimization:** Tools to clean temporary files, manage startup programs, adjust power settings, and more (some features pending full implementation).
*   **Configuration Management:** Centralized settings via `config/config.ini`.
*   **System Monitoring:** Real-time insights into system performance (under development).
*   **Internationalization (i18n):** Support for multiple languages (via `locales/`).
*   **Accessibility:** Designed with accessibility considerations.
*   **Feature Flags:** Allows for controlled rollout of new capabilities.

## 🚀 Getting Started

### Option 1: Download the Executable (Recommended)

The easiest way to use SentinelPC is to download the pre-built executable:

1.  Go to the **Latest Release** page.
2.  Download the `SentinelPC.exe` file from the Assets section.
3.  Save the `.exe` file to a convenient location on your computer.
4.  No installation is required! Proceed to the Usage section.

*Note: Due to a temporary CI issue (see `WORKAROUND.md`), automated builds might be paused. If no `.exe` is available, please use Option 2 or check back later.*

### Option 2: Running from Source (For Development/Testing)

If you want to run the latest development code or contribute:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/johnwesleyquintero/SentinelPC.git
    cd SentinelPC
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    *   **GUI:** `python src/sentinel_gui.py`
    *   **CLI:** `python src/sentinel_cli.py`

## 💻 Usage

1.  **Run the application:**
    *   If you downloaded the executable: Double-click `SentinelPC.exe` or run it from your terminal:
        ```bash
        .\dist\SentinelPC.exe 
        ```
    *   If running from source, use the Python commands mentioned in Option 2.

2.  **Choose Interface Mode (Optional):**
    By default, SentinelPC might launch the GUI. You can force a specific mode using flags (primarily for the `.exe`):
    ```bash
    # Force CLI mode
    .\SentinelPC.exe --cli

    # Force GUI mode
    .\SentinelPC.exe --gui
    ```

3.  **Configuration:**
    Adjust application settings by editing the `config/config.ini` file.

## 🛠️ Building from Source

If you need to build the `SentinelPC.exe` yourself:

1.  Ensure you have followed steps 1-2 from Option 2.
2.  Install development dependencies:
    ```bash
    pip install -r requirements-dev.txt
    ```
3.  Run the unified build script:
    ```bash
    python scripts/build_unified.py
    ```
4.  The executable will be created in the `dist/` directory.

*Note: See `WORKAROUND.md` for details on the current manual build process if CI is unavailable.*

## ⚙️ Known Issues and Workarounds

Due to a temporary issue with the CI service, automated builds and releases may be unavailable. Please refer to the `WORKAROUND.md` file for instructions on local development, manual building, and manual release procedures.

## 📂 Project Structure

SentinelPC/
├── .github/ # GitHub Actions workflows
├── _wwwroot/ # Static website/landing page assets
├── build/ # PyInstaller build artifacts (temporary)
├── config/ # Configuration files (config.ini)
├── dist/ # Distribution executables (output of build)
├── docs/ # Project documentation
├── locales/ # Internationalization files (e.g., .po, .mo)
├── scripts/ # Build and utility scripts (build_unified.py)
├── spec/ # PyInstaller spec files
├── src/ # Main source code
│   ├── cli/ # Command-line interface logic
│   ├── core/ # Core functionalities (optimizer, config, etc.)
│   ├── gui/ # Graphical user interface logic
│   └── ... # Other shared modules/packages
├── tests/ # Unit and integration tests
├── .gitignore # Git ignore rules
├── CONTRIBUTING.md # Guidelines for contributors
├── LICENSE # Project license (MIT)
├── README.md # This file
├── requirements-dev.txt # Development dependencies
├── requirements.txt # Core application dependencies
├── TODO.md # Project roadmap and tasks
└── WORKAROUND.md # Temporary workaround info

## 🤝 Contributing

Contributions are welcome! Please read the `CONTRIBUTING.md` file for guidelines on setting up your development environment, code style, testing procedures, and submitting pull requests.

## 🐛 Troubleshooting

*   **ModuleNotFoundError:** Ensure you are in your activated virtual environment (`venv`) and have installed dependencies using `pip install -r requirements.txt`.
*   **File Not Found:** Verify that relative paths in configuration or code are correct based on the project structure.
*   **Build Errors:** Check the output from the build script (`build_unified.py`) and ensure development dependencies (`requirements-dev.txt`) are installed. Consult `WORKAROUND.md` if CI issues persist.
*   **Other Issues:** Check the application logs (e.g., `SentinelPC.log` if implemented) or open an issue on GitHub.

## 📜 License

This project is licensed under the MIT License - see the `LICENSE` file for details.

For future enhancements and project roadmap, please refer to the `TODO.md` file.
