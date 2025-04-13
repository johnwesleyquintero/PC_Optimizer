#!/usr/bin/env python3

import PyInstaller.__main__
import os
import shutil
from pathlib import Path

def clean_build_dirs():
    """Clean build and dist directories"""
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)

def build_unified_app():
    """Build unified SentinelPC application"""
    PyInstaller.__main__.run([
        'src/main.py',                    # Main script
        '--name=SentinelPC',              # Output name
        '--onefile',                      # Single file output
        '--windowed',                     # GUI mode support
        '--icon=Assets/Branding/icon.ico', # Application icon
        '--add-data=config/config.ini;config', # Include config
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
    
    # Clean previous builds
    clean_build_dirs()
    
    # Build application
    build_unified_app()
    
    print("\nBuild complete! Output in 'dist' directory")
    print("Run 'SentinelPC.exe' for GUI mode")
    print("Run 'SentinelPC.exe --cli' for CLI mode")

if __name__ == '__main__':
    main()