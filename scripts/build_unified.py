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

def clean_build_dirs(max_retries=3, retry_delay=2):
    """Clean build and dist directories with retry mechanism for locked files
    
    Args:
        max_retries (int): Maximum number of cleanup attempts
        retry_delay (int): Delay in seconds between retries
    
    Returns:
        bool: True if cleanup successful, False otherwise
    """
    import time
    from pathlib import Path
    
    try:
        # Get the project root directory
        project_root = Path(__file__).parent.parent
        
        # Clean build and dist directories
        for dir_name in ['build', 'dist']:
            dir_path = project_root / dir_name
            if not dir_path.exists():
                continue
                
            for attempt in range(max_retries):
                try:
                    print(f"Attempting to clean {dir_name} directory (attempt {attempt + 1}/{max_retries})")
                    if dir_path.exists():
                        shutil.rmtree(dir_path)
                    # Create fresh directory
                    dir_path.mkdir(exist_ok=True)
                    break
                except PermissionError as pe:
                    if attempt < max_retries - 1:
                        print(f"Directory {dir_name} is locked. Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    else:
                        print(f"Failed to clean {dir_name} directory after {max_retries} attempts.")
                        print("Please close any applications that might be using these files and try again.")
                        return False
                except Exception as e:
                    print(f"Unexpected error cleaning {dir_name} directory: {str(e)}")
                    return False
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