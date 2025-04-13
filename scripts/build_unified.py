#!/usr/bin/env python3

import PyInstaller.__main__
import os
import shutil
import sys
import subprocess
from pathlib import Path

ICON_PATH = os.path.join('_wwwroot', 'Assets', 'Branding', 'favicon.ico')

def verify_environment():
    """Verify Python environment and dependencies"""
    try:
        # Check if running in virtual environment
        in_venv = sys.prefix != sys.base_prefix
        if not in_venv:
            print("Warning: Not running in a virtual environment")
        
        # Verify icon file exists
        if not os.path.exists(ICON_PATH):
            print(f"Warning: Icon file not found at {ICON_PATH}")
            
        # Verify PyInstaller installation
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print("Successfully installed requirements")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to install requirements: {e}")
            return False
    except Exception as e:
        print(f"Environment setup failed: {str(e)}")
        return False

def clean_build_dirs():
    """Clean build and dist directories"""
    try:
        # Get the project root directory
        project_root = Path(__file__).parent.parent
        
        # Clean build and dist directories
        for dir_name in ['build', 'dist']:
            dir_path = project_root / dir_name
            if dir_path.exists():
                shutil.rmtree(dir_path)
            # Create fresh directory
            dir_path.mkdir(exist_ok=True)
        return True
    except Exception as e:
        print(f"Failed to clean directories: {str(e)}")
        return False

def build_unified_app():
    """Build unified SentinelPC application"""
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    
    # Ensure required directories exist
    dist_dir = project_root / 'dist'
    dist_dir.mkdir(exist_ok=True)

    icon_path = project_root / 'src' / 'gui' / 'assets' / 'icon.ico'
    print(f"Icon path: {icon_path}")
    if not icon_path.exists():
        print(f"Warning: Icon file not found at {icon_path}. Building without an icon.")
        icon_arg = ""
    else:
        print(f"Icon file exists: {icon_path}")
        icon_arg = f"--icon={icon_path}"

    PyInstaller.__main__.run([
        'src/main.py',                    # Main script
        '--name=SentinelPC',              # Output name
        '--onefile',                      # Single file output
        '--windowed',                     # GUI mode support
        f'--icon={ICON_PATH}',            # Application icon
        '--add-data=config/*.ini;config', # Include config
        '--add-data=locales/*.json;locales', # Include locales
        '--clean',                        # Clean cache
        '--noconfirm',                    # Overwrite existing
        # Add necessary imports
        '--hidden-import=tkinter',
        '--hidden-import=PIL',
        # Exclude unnecessary modules
        '--exclude-module=test',
        '--exclude-module=unittest',
    ])

def main():
    print("Building unified SentinelPC application...")
    
    # Verify environment
    if not verify_environment():
        print("Environment verification failed")
        sys.exit(1)
    
    # Clean previous builds
    if not clean_build_dirs():
        print("Failed to clean build directories")
        sys.exit(1)
    
    try:
        # Build application
        build_unified_app()
        print("\nBuild complete! Output in 'dist' directory")
        print("Run 'SentinelPC.exe' for GUI mode")
        print("Run 'SentinelPC.exe --cli' for CLI mode")
    except Exception as e:
        print(f"Build failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()