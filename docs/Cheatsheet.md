# Development Command Cheatsheet


```bash
.\run_tasks.bat
```

This file provides common commands used during the development of SentinelPC. Copy and paste these into your terminal (like Command Prompt, PowerShell, or Git Bash on Windows).

**Remember to activate your virtual environment first for most commands!**

## 1. Initial Project Setup

*These commands are typically run only once when setting up the project.*

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/johnwesleyquintero/SentinelPC.git
cd SentinelPC

# Create a virtual environment named 'venv'
python -m venv venv

# Activate the virtual environment
# On Windows (Command Prompt/PowerShell):
venv\Scripts\activate.bat
# On macOS/Linux (Bash/Zsh):
# source venv/bin/activate

# Install required dependencies for running the app
pip install -r requirements.txt

# Install additional dependencies for development (testing, building, linting)
pip install -r requirements-dev.txt
```

## 2. Running the Application (from Source Code)
Use these commands to run the application directly from the source files for testing and debugging.

```bash
# Run the main application (usually defaults to GUI)
python -m src.main

# Explicitly run the GUI (if main doesn't default)
# python src/sentinel_gui.py # Adjust path if needed

# Explicitly run the CLI (if main doesn't default or for specific CLI testing)
# python src/sentinel_cli.py # Adjust path if needed
```

## 3. Building the Executable
Use these commands to package the application into a standalone .exe file.

```bash
# Run the standard build script (uses PyInstaller via SentinelPC.spec)
python scripts/build_unified.py

# --- OR ---

# Run PyInstaller directly using the spec file (for debugging build issues)
pyinstaller SentinelPC.spec
```

The output executable (SentinelPC.exe) will be located in the dist/ directory.

## 4. Running the Built Executable
After building, use these commands to test the packaged .exe.

```bash
# Run the executable (usually defaults to GUI)
.\dist\SentinelPC.exe

# Force run in CLI mode
.\dist\SentinelPC.exe --cli

# Force run in GUI mode
.\dist\SentinelPC.exe --gui
```

## 5. Code Quality Checks
Run these tools to ensure code style and quality.

```bash
# Check for style issues with Flake8
flake8 src/ tests/

# Format code automatically with Black (run this before committing)
black src/ tests/
```

## 6. Automated Task Runner (SentinelPC X WESCORE)
This script combines several common development steps into one command.

```bash
# Runs the enhanced task runner:
# 1. Kills existing SentinelPC.exe
# 2. Runs Flake8 (logs to run_tasks.log)
# 3. Runs Black (logs to run_tasks.log)
# 4. Builds the executable (logs to run_tasks.log)
# 5. Runs the built SentinelPC.exe
# Check run_tasks.log for detailed output, especially on errors.
.\run_tasks.bat
```

## 7. Utility / Troubleshooting Commands
Helpful commands for common development issues.

```bash
# Force kill the SentinelPC process if it's stuck (Windows)
taskkill /F /IM SentinelPC.exe

# Workaround for potential PyInstaller issues (reinstall without dependencies)
pip install --upgrade --no-deps --force-reinstall pyinstaller