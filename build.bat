@echo off
echo Building SentinelPC...

:: Check if running in a virtual environment (optional, but good practice)
if "%VIRTUAL_ENV%"=="" (
    echo Warning: Not running in a virtual environment.
)

:: Activate the virtual environment
call venv\Scripts\activate

:: Install requirements
python -m pip install -r requirements.txt

:: Run the build script
python scripts\build_unified.py

:: Deactivate the virtual environment
:: Example:
:: deactivate

pause