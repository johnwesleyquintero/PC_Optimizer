@echo off
setlocal enabledelayedexpansion

:: --- Configuration ---
set SCRIPT_DIR=%~dp0
set VENV_DIR=%SCRIPT_DIR%venv
set PYTHON_EXE=python
set REQUIREMENTS_FILE=%SCRIPT_DIR%requirements-build.txt
set MAIN_MODULE=src.main
:: You might need to adjust MAIN_MODULE if your entry point is different
:: e.g., set MAIN_SCRIPT=%SCRIPT_DIR%src\main.py

set VENV_ACTIVATED=0
set ERROR_CODE=0

echo ==================================
echo Starting SentinelPC Application Runner
echo ==================================
echo.

:: --- Check for Python ---
echo Checking for Python installation...
where %PYTHON_EXE% >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: '%PYTHON_EXE%' command not found in PATH.
    echo Please install Python and ensure it's added to your system PATH.
    goto error_exit
)
echo Found Python:
where %PYTHON_EXE%
echo.

:: --- Check/Create Virtual Environment ---
echo Checking for virtual environment at: %VENV_DIR%
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Virtual environment not found. Attempting to create it...
    %PYTHON_EXE% -m venv "%VENV_DIR%"
    if !errorlevel! neq 0 (
        echo ERROR: Failed to create the virtual environment in "%VENV_DIR%".
        echo Check permissions and available disk space.
        goto error_exit
    )
    echo Virtual environment created successfully.
) else (
    echo Virtual environment found. Reusing existing environment.
)
echo.

:: --- Activate Virtual Environment ---
echo Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"
if !errorlevel! neq 0 (
    echo ERROR: Failed to activate the virtual environment.
    echo Ensure the venv is not corrupted. You might need to delete the '%VENV_DIR%' folder and retry.
    goto error_exit
)
set VENV_ACTIVATED=1
echo Virtual environment activated.
echo Python executable in venv:
where python
echo.

:: --- Check for Requirements File ---
echo Checking for requirements file: %REQUIREMENTS_FILE%
if not exist "%REQUIREMENTS_FILE%" (
    echo ERROR: Requirements file not found at "%REQUIREMENTS_FILE%".
    goto error_exit
)
echo Requirements file found.
echo.

:: --- Install/Update Requirements ---
echo Installing/updating dependencies from %REQUIREMENTS_FILE%...
python -m pip install -r "%REQUIREMENTS_FILE%"
if !errorlevel! neq 0 (
    echo ---------------------------------------------------------------------
    echo ERROR: Failed to install dependencies using pip.
    echo Possible Causes:
    echo   - Network connection issues (check internet).
    echo   - Invalid package name or version in '%REQUIREMENTS_FILE%'.
    echo   - Missing build tools (like C++ compiler) required by some packages.
    echo     Look for errors mentioning 'compiler', 'cl.exe', 'gcc', 'meson', 'build failed'.
    echo     If found, install 'Microsoft C++ Build Tools' via Visual Studio Installer.
    echo   - Insufficient permissions.
    echo Check the detailed pip output above for specific error messages.
    echo ---------------------------------------------------------------------
    goto error_exit
)
echo Dependencies installed/updated successfully.
echo.

:: --- Run the Application ---
echo Running the application: python -m %MAIN_MODULE%
python -m %MAIN_MODULE%
if !errorlevel! neq 0 (
    echo ERROR: The application (%MAIN_MODULE%) exited with an error code: !errorlevel!.
    echo Check the application's output above for details.
    goto error_exit
)
echo Application finished execution.
echo.

:: --- Success Exit ---
echo ==================================
echo Application run completed.
echo ==================================
goto cleanup

:error_exit
echo.
echo ==================================
echo SCRIPT FAILED!
echo ==================================
set ERROR_CODE=1
goto cleanup

:cleanup
echo.
if %VENV_ACTIVATED% equ 1 (
    echo Deactivating virtual environment...
    call deactivate >nul 2>&1
    rem Added >nul 2>&1 to suppress potential "deactivate is not recognized" if env wasn't fully set up
) else (
    echo No virtual environment was activated by this script.
)

echo Exiting run script.
pause
exit /b %ERROR_CODE%

endlocal
