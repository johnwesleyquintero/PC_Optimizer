@echo off
setlocal enabledelayedexpansion

:: --- Configuration ---
set SCRIPT_DIR=%~dp0
set VENV_DIR=%SCRIPT_DIR%venv
set PYTHON_EXE=python
set REQUIREMENTS_FILE=%SCRIPT_DIR%requirements-build.txt
set BUILD_PY_SCRIPT=%SCRIPT_DIR%scripts\build_unified.py
set VENV_ACTIVATED=0
set ERROR_CODE=0

echo ==================================
echo Starting SentinelPC Build Process
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
    echo Virtual environment found.
)
echo.

:: --- Activate Virtual Environment ---
echo Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"
if !errorlevel! neq 0 (
    echo ERROR: Failed to activate the virtual environment.
    goto error_exit
)
set VENV_ACTIVATED=1
echo Virtual environment activated.
echo Python executable in venv:
where python
echo Pip executable in venv:
where pip
echo.

:: --- Upgrade Core Packaging Tools ---
echo Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel
if !errorlevel! neq 0 (
    echo WARNING: Failed to upgrade pip/setuptools/wheel. Continuing anyway...
    rem Decide if this should be a fatal error - usually it's okay to continue
    rem goto error_exit
) else (
    echo Core packaging tools upgraded successfully.
)
echo.


:: --- Check for Requirements File ---
echo Checking for requirements file: %REQUIREMENTS_FILE%
if not exist "%REQUIREMENTS_FILE%" (
    echo ERROR: Requirements file not found at "%REQUIREMENTS_FILE%".
    goto error_exit
)
echo Requirements file found.
echo.

:: --- Install Requirements ---
echo Installing dependencies from %REQUIREMENTS_FILE%...
python -m pip install -r "%REQUIREMENTS_FILE%"
if !errorlevel! neq 0 (
    echo ---------------------------------------------------------------------
    echo ERROR: Failed to install dependencies using pip.
    echo Possible Causes:
    echo   - Network connection issues (check internet).
    echo   - Invalid package name or version in '%REQUIREMENTS_FILE%'.
    echo   - Missing build tools (like C++ compiler) required by some packages (e.g., numpy, pandas).
    echo     Look for errors mentioning 'compiler', 'cl.exe', 'gcc', 'meson', 'build failed'.
    echo     If found, install 'Microsoft C++ Build Tools' via Visual Studio Installer.
    echo   - Insufficient permissions.
    echo Check the detailed pip output above for specific error messages.
    echo ---------------------------------------------------------------------
    goto error_exit
)
echo Dependencies installed successfully.
echo.

:: --- Check for Build Script ---
echo Checking for build script: %BUILD_PY_SCRIPT%
if not exist "%BUILD_PY_SCRIPT%" (
    echo ERROR: Build script not found at "%BUILD_PY_SCRIPT%".
    goto error_exit
)
echo Build script found.
echo.

:: --- Run Build Script ---
echo Running the build script: %BUILD_PY_SCRIPT%
python "%BUILD_PY_SCRIPT%"
if !errorlevel! neq 0 (
    echo ERROR: The Python build script ('%BUILD_PY_SCRIPT%') exited with an error.
    echo Check the output from the script above for details.
    goto error_exit
)
echo Build script executed successfully.
echo.

:: --- Success Exit ---
echo ==================================
echo Build process completed successfully!
echo ==================================
goto cleanup

:error_exit
echo.
echo ==================================
echo BUILD FAILED!
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

echo Exiting build process.
endlocal
pause
exit /b %ERROR_CODE%
