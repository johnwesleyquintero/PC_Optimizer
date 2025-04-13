#!/usr/bin/env python3

import PyInstaller.__main__
import os
import sys
from pathlib import Path
import shutil

def verify_environment():
    """Verify build environment requirements"""
    try:
        # Check for required directories
        required_dirs = ['src', 'config', 'locales']
        for dir_name in required_dirs:
            if not os.path.isdir(dir_name):
                print(f"Error: Required directory '{dir_name}' not found")
                return False
        
        # Check for main script
        if not os.path.isfile('src/main.py'):
            print("Error: src/main.py not found")
            return False
            
        return True
    except Exception as e:
        print(f"Environment verification failed: {str(e)}")
        return False

ICON_PATH = os.path.join('_wwwroot', 'Assets', 'Branding', 'icon.ico')

def build_executable():
    """Build the SentinelPC executable"""
    try:
        args = [
            'src/main.py',
            '--name=SentinelPC',
            '--onefile',
            '--clean'
        ]
        if os.path.exists(ICON_PATH):
            args.extend(['--icon', ICON_PATH])
        args.extend(['--add-data', 'config/*.ini:config'])
        args.extend(['--hidden-import', 'numpy'])
        args.extend(['--hidden-import', 'pandas'])
        PyInstaller.__main__.run(args)
        print("Build completed successfully!")
        return True
    except Exception as e:
        print(f"Build failed: {str(e)}")
        return False

if __name__ == '__main__':
    build_executable()

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

    # Convert paths to absolute paths
    main_script = str(project_root / 'src' / 'main.py')
    config_path = str(project_root / 'config')
    locales_path = str(project_root / 'locales')

    # Build PyInstaller arguments
    args = [
        main_script,                      # Main script
        '--name=SentinelPC',              # Output name
        '--onefile',                      # Single file output
        '--windowed',                     # GUI mode support
        icon_arg,                         # Application icon
        f'--add-data={config_path}/*.ini{os.pathsep}config',  # Include config
        f'--add-data={locales_path}/*.json{os.pathsep}locales',  # Include locales
        '--clean',                        # Clean cache
        '--noconfirm',                    # Overwrite existing
        '--hidden-import=tkinter',        # Add necessary imports
        '--hidden-import=PIL',
        '--exclude-module=test',          # Exclude unnecessary modules
        '--exclude-module=unittest'
    ]

    # Filter out empty arguments
    args = [arg for arg in args if arg]

    # Run PyInstaller
    PyInstaller.__main__.run(args)

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