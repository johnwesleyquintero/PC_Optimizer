@echo off
echo Building SentinelPC Application...

:: Set Python environment
set PYTHON=python

:: Clean previous builds
if exist "dist" rd /s /q "dist"
if exist "build" rd /s /q "build"

:: Install required packages
%PYTHON% -m pip install -r requirements.txt

:: Build the consolidated SentinelPC application
%PYTHON% -m PyInstaller SentinelPC.spec --clean --noconfirm

if %ERRORLEVEL% NEQ 0 (
    echo Build failed!
    exit /b 1
)

echo Build completed successfully!
echo Executable can be found in the dist directory.
