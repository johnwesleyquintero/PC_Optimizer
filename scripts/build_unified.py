#!/usr/bin/env python3

import os
import sys
import shutil
import time
import platform
import re
from pathlib import Path
import subprocess # Using subprocess for better control over PyInstaller execution/output

# --- Configuration ---
try:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
except NameError:
    # Handle case where __file__ is not defined (e.g., interactive interpreter)
    PROJECT_ROOT = Path('.').resolve()

APP_NAME = "SentinelPC"
MAIN_SCRIPT_REL = Path("src") / "main.py" # Relative path to main script
ICON_REL = Path("src") / "gui" / "assets" / "icon.ico" # Relative path to icon

# Directories (relative to PROJECT_ROOT)
SRC_DIR_REL = Path("src")
CONFIG_DIR_REL = Path("config")
LOCALES_DIR_REL = Path("locales")
DIST_DIR_REL = Path("dist")
BUILD_DIR_REL = Path("build") # PyInstaller's working directory

# PyInstaller settings
USE_ONEFILE = True # Set to False for --onedir (folder output, often better for debugging)
USE_WINDOWED = True # Set to False for console applications or easier debugging
CLEAN_PYINSTALLER_CACHE = True # Use --clean flag
CONFIRM_OVERWRITE = False # Use --noconfirm flag
HIDDEN_IMPORTS = [
    'tkinter',
    'PIL',
    # Add other necessary hidden imports discovered during testing
    # 'numpy', # Uncomment if needed
    # 'pandas', # Uncomment if needed
]
EXCLUDE_MODULES = [
    'test',
    'unittest',
    'pytest',
    # Add other modules to exclude if known
]
# Optional: Path to UPX executable if you want to use it for compression
# UPX_DIR = Path("C:/path/to/upx") # Example: Set to None to disable
UPX_DIR = None

# --- Helper Functions ---

def get_project_version() -> str:
    """Reads the version from pyproject.toml"""
    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    default_version = "0.0.0"
    if not pyproject_path.is_file():
        print(f"Warning: pyproject.toml not found at {pyproject_path}. Using default version '{default_version}'.")
        return default_version
    try:
        with open(pyproject_path, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
            if match:
                version = match.group(1)
                print(f"Found version in pyproject.toml: {version}")
                return version
            else:
                print(f"Warning: Could not find version pattern in {pyproject_path}. Using default version '{default_version}'.")
                return default_version
    except Exception as e:
        print(f"Error reading version from {pyproject_path}: {e}. Using default version '{default_version}'.")
        return default_version

def run_command(command, cwd=None, check=True):
    """Runs a shell command using subprocess, capturing output."""
    if cwd is None:
        cwd = PROJECT_ROOT
    print(f"\n--- Running Command ---")
    print(f"Directory: {cwd}")
    print(f"Command: {' '.join(map(str, command))}")
    print("-----------------------")
    try:
        # Use sys.executable to ensure we're using the Python from the active venv
        process = subprocess.run([sys.executable] + command, cwd=cwd, check=check, capture_output=True, text=True, encoding='utf-8')
        if process.stdout:
            print("--- STDOUT ---")
            print(process.stdout.strip())
            print("--------------")
        if process.stderr:
            # PyInstaller often prints informational messages to stderr
            print("--- STDERR ---")
            print(process.stderr.strip())
            print("--------------")
        print("--- Command finished successfully ---")
        return process
    except subprocess.CalledProcessError as e:
        print(f"--- ERROR running command ---")
        print(f"Return Code: {e.returncode}")
        if e.stdout:
            print("--- STDOUT ---")
            print(e.stdout.strip())
            print("--------------")
        if e.stderr:
            print("--- STDERR ---")
            print(e.stderr.strip())
            print("--------------")
        # Re-raise the exception to stop the build if check=True
        if check:
            raise
        return None
    except FileNotFoundError:
        print(f"--- ERROR: Command not found: {command[0]} ---")
        print("Ensure PyInstaller is installed in the virtual environment and accessible.")
        print(f"Attempted Python executable: {sys.executable}")
        raise
    except Exception as e:
        print(f"--- An unexpected error occurred running the command: {e} ---")
        raise

def clean_directory(dir_path: Path, max_retries=3, retry_delay=2):
    """Removes and recreates a directory with retry logic."""
    if not dir_path.exists():
        print(f"Directory not found, skipping cleanup: {dir_path}")
        # Ensure it exists for later steps
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {dir_path}")
        except Exception as e:
            print(f"Error creating directory {dir_path}: {e}")
            return False
        return True

    print(f"Attempting to clean directory: {dir_path}")
    for attempt in range(max_retries):
        try:
            shutil.rmtree(dir_path)
            print(f"Successfully removed directory: {dir_path}")
            # Recreate the directory immediately after successful removal
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"Successfully recreated directory: {dir_path}")
            return True
        except PermissionError as pe:
            print(f"Attempt {attempt + 1}/{max_retries}: PermissionError cleaning {dir_path}. File likely locked.")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Failed to clean {dir_path} after {max_retries} attempts due to PermissionError.")
                print("Possible causes: Antivirus scanning, file explorer open, application still running.")
                print("Please close any relevant programs and try again.")
                return False
        except FileNotFoundError:
            print(f"Directory {dir_path} was not found during cleanup attempt (might have been deleted already).")
            # Try to recreate it
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"Successfully recreated directory: {dir_path}")
                return True
            except Exception as e:
                 print(f"Error creating directory {dir_path} after FileNotFoundError: {e}")
                 return False
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries}: Unexpected error cleaning {dir_path}: {e}")
            if attempt < max_retries - 1:
                 print(f"Retrying in {retry_delay} seconds...")
                 time.sleep(retry_delay)
            else:
                print(f"Failed to clean {dir_path} after {max_retries} attempts due to unexpected error.")
                return False
    return False # Should not be reached if logic is correct, but acts as a safeguard

def verify_environment():
    """Verify build environment requirements."""
    print("\n--- Verifying Environment ---")
    all_ok = True
    # Check for required directories relative to project root
    required_dirs = [SRC_DIR_REL, CONFIG_DIR_REL, LOCALES_DIR_REL]
    for dir_rel in required_dirs:
        dir_abs = PROJECT_ROOT / dir_rel
        if not dir_abs.is_dir():
            print(f"Error: Required directory not found: {dir_abs}")
            all_ok = False
        else:
            print(f"Found directory: {dir_abs}")

    # Check for main script
    main_script_abs = PROJECT_ROOT / MAIN_SCRIPT_REL
    if not main_script_abs.is_file():
        print(f"Error: Main script not found: {main_script_abs}")
        all_ok = False
    else:
        print(f"Found main script: {main_script_abs}")

    # Check for PyInstaller (basic import check)
    try:
        import PyInstaller
        print(f"Found PyInstaller version: {getattr(PyInstaller, '__version__', 'unknown')}")
    except ImportError:
        print("Error: PyInstaller module not found.")
        print("Please ensure PyInstaller is installed in your virtual environment:")
        print(f"  pip install pyinstaller")
        all_ok = False

    if all_ok:
        print("Environment verification successful.")
    else:
        print("Environment verification FAILED.")
    print("---------------------------")
    return all_ok

def build_with_pyinstaller():
    """Build the executable using PyInstaller."""
    print("\n--- Starting PyInstaller Build ---")

    # --- Calculate Absolute Paths ---
    main_script_abs = PROJECT_ROOT / MAIN_SCRIPT_REL
    dist_dir_abs = PROJECT_ROOT / DIST_DIR_REL
    build_dir_abs = PROJECT_ROOT / BUILD_DIR_REL
    icon_abs = PROJECT_ROOT / ICON_REL
    config_dir_abs = PROJECT_ROOT / CONFIG_DIR_REL
    locales_dir_abs = PROJECT_ROOT / LOCALES_DIR_REL

    # --- Clean Build/Dist Directories ---
    print("Cleaning previous build artifacts...")
    if not clean_directory(build_dir_abs): return False
    if not clean_directory(dist_dir_abs): return False
    print("Cleaning complete.")

    # --- Prepare PyInstaller Arguments ---
    pyinstaller_args = [
        "-m", "PyInstaller", # Run PyInstaller as a module
        str(main_script_abs),
        f"--name={APP_NAME}",
        f"--distpath={dist_dir_abs}",
        f"--workpath={build_dir_abs}",
    ]

    # Output type (--onefile or --onedir)
    if USE_ONEFILE:
        pyinstaller_args.append("--onefile")
        print("Build type: Single File Executable (--onefile)")
    else:
        pyinstaller_args.append("--onedir")
        print("Build type: Folder with Dependencies (--onedir)")

    # Console/Windowed mode
    if USE_WINDOWED:
        # On Windows, --windowed implies --noconsole
        pyinstaller_args.append("--windowed")
        print("Mode: Windowed GUI Application (--windowed)")
    else:
        # Explicitly use --console (default, but good for clarity)
        pyinstaller_args.append("--console")
        print("Mode: Console Application (--console)")

    # Icon
    if icon_abs.is_file():
        pyinstaller_args.extend(["--icon", str(icon_abs)])
        print(f"Using icon: {icon_abs}")
    else:
        print(f"Warning: Icon file not found at {icon_abs}. Building without custom icon.")

    # Add Data Files (config, locales)
    # Syntax: --add-data "SOURCE{os.pathsep}DESTINATION_IN_BUNDLE"
    # Using Path objects ensures correct path separators for the OS where the script runs
    # PyInstaller normalizes separators for the target OS internally.
    if config_dir_abs.is_dir():
        # Add all .ini files from the config directory to a 'config' folder in the bundle
        pyinstaller_args.append(f"--add-data={config_dir_abs}{os.pathsep}config")
        print(f"Adding data: {config_dir_abs} -> config/")
    else:
        print(f"Warning: Config directory not found at {config_dir_abs}. Not adding config files.")

    if locales_dir_abs.is_dir():
        # Add all .json files from the locales directory to a 'locales' folder in the bundle
        pyinstaller_args.append(f"--add-data={locales_dir_abs}{os.pathsep}locales")
        print(f"Adding data: {locales_dir_abs} -> locales/")
    else:
        print(f"Warning: Locales directory not found at {locales_dir_abs}. Not adding locale files.")

    # Hidden Imports
    for imp in HIDDEN_IMPORTS:
        pyinstaller_args.extend(["--hidden-import", imp])
    if HIDDEN_IMPORTS:
        print(f"Adding hidden imports: {', '.join(HIDDEN_IMPORTS)}")

    # Excluded Modules
    for mod in EXCLUDE_MODULES:
        pyinstaller_args.extend(["--exclude-module", mod])
    if EXCLUDE_MODULES:
        print(f"Excluding modules: {', '.join(EXCLUDE_MODULES)}")

    # Other flags
    if CLEAN_PYINSTALLER_CACHE:
        pyinstaller_args.append("--clean")
        print("Enabled: Clean PyInstaller cache (--clean)")
    if not CONFIRM_OVERWRITE:
        pyinstaller_args.append("--noconfirm")
        print("Enabled: Overwrite output without confirmation (--noconfirm)")

    # UPX Compression (Optional)
    if UPX_DIR and UPX_DIR.is_dir():
        pyinstaller_args.extend(["--upx-dir", str(UPX_DIR)])
        print(f"Enabled: UPX compression using directory: {UPX_DIR}")
    elif UPX_DIR:
        print(f"Warning: UPX directory specified but not found: {UPX_DIR}. Skipping UPX.")

    # --- Execute PyInstaller ---
    try:
        # Using subprocess to run PyInstaller via the current Python interpreter
        run_command(pyinstaller_args, cwd=PROJECT_ROOT, check=True)
        print("\n--- PyInstaller Build Successful ---")
        print(f"Output located in: {dist_dir_abs}")
        # Provide specific executable path based on build type
        if USE_ONEFILE:
            exe_path = dist_dir_abs / f"{APP_NAME}.exe"
            print(f"Executable: {exe_path}")
        else:
            exe_path = dist_dir_abs / APP_NAME / f"{APP_NAME}.exe"
            print(f"Output folder: {dist_dir_abs / APP_NAME}")
            print(f"Executable inside folder: {exe_path}")

        # Note about CLI mode if built as windowed
        if USE_WINDOWED:
             print("\nNote: Built as a windowed application.")
             print("If your application supports a '--cli' mode, it needs to handle console")
             print("attachment internally if started from a command prompt with that flag.")

        return True
    except subprocess.CalledProcessError:
        print("\n--- PyInstaller Build FAILED ---")
        print("Check the output/errors above for details.")
        print("Common issues:")
        print("  - Missing hidden imports (check PyInstaller warnings/errors).")
        print("  - Incorrectly specified data files.")
        print("  - Conflicts with antivirus software (try temporarily disabling or excluding build folders).")
        print("  - Insufficient permissions to write to build/dist directories.")
        return False
    except Exception as e:
        print(f"\n--- An unexpected error occurred during the PyInstaller execution: {e} ---")
        import traceback
        traceback.print_exc()
        return False

# --- Main Execution ---
def main():
    """Main build process orchestration."""
    start_time = time.time()
    print("=======================================")
    print(f" Starting Unified Build Script for {APP_NAME}")
    print(f" Project Root: {PROJECT_ROOT}")
    print(f" Platform: {platform.system()} ({platform.release()})")
    print(f" Python: {sys.version}")
    print(f" Script: {__file__}")
    print("=======================================")

    # 1. Verify Environment
    if not verify_environment():
        sys.exit(1) # Exit if basic requirements are not met

    # 2. Get Version (Optional but good practice)
    project_version = get_project_version()
    # You could potentially pass this version to PyInstaller using a version file
    # or by generating a spec file first, but we'll keep it simple for now.

    # 3. Run the Build
    success = build_with_pyinstaller()

    # 4. Conclude
    end_time = time.time()
    duration = end_time - start_time
    print("\n=======================================")
    if success:
        print(f" Build Finished Successfully in {duration:.2f} seconds")
        print(" Please test the application thoroughly.")
        print(" Potential issues to check:")
        print("   - Antivirus false positives (especially with --onefile).")
        print("   - Missing data files (config, locales, assets).")
        print("   - GUI scaling issues on high-DPI displays.")
        print("   - Functionality requiring specific system libraries.")
        print("=======================================")
        sys.exit(0) # Exit with success code
    else:
        print(f" Build FAILED after {duration:.2f} seconds")
        print("=======================================")
        sys.exit(1) # Exit with error code

if __name__ == "__main__":
    # Ensure the script's directory is the working directory
    # This helps if the script is called from elsewhere but relies on relative paths
    # Note: PROJECT_ROOT is already absolute, so this mainly affects relative file access
    # if any were used directly without joining with PROJECT_ROOT.
    os.chdir(PROJECT_ROOT)
    print(f"Changed working directory to: {os.getcwd()}")
    main()
