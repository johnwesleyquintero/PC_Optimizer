@echo off
pip install pyinstaller

@echo Cleaning previous builds
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

@echo Uninstalling conflicting pathlib package
"C:\Python313\python.exe" -m pip uninstall -y pathlib

@echo Building SentinelPC
pyinstaller --onefile --name SentinelPC ^
  --icon=wwwroot\Assets\Branding\app_icon.ico ^
  --hidden-import config_manager_v2 ^
  --hidden-import performance_optimizer_v2 ^
  --paths=src/core ^
  --distpath ./dist ^
  --workpath ./build ^
  main.py
