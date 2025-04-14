@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

:: ####################################
:: SentinelPC X WESCORE | Enhanced Development Task Runner
:: ####################################
:: Runs common development tasks in sequence with logging and improved error handling:
:: 1. Kill existing process (if any)
:: 2. Check code style (Flake8) -> Logs to run_tasks.log
:: 3. Format code (Black) -> Logs to run_tasks.log
:: 4. Build executable (PyInstaller via script) -> Logs to run_tasks.log
:: 5. Run the built executable
::
:: Log file: run_tasks.log (created/overwritten in the project root)
:: ####################################

SET LOGFILE=run_tasks.log
ECHO Starting SentinelPC Task Runner Log > %LOGFILE%
ECHO Timestamp: %DATE% %TIME% >> %LOGFILE%
ECHO ======================================== >> %LOGFILE%
ECHO.

ECHO [1/5] Attempting to kill any running SentinelPC.exe process...
taskkill /F /IM SentinelPC.exe > nul 2>&1
ECHO      Kill attempt logged (Success/Failure not critical here). >> %LOGFILE%
ECHO      Done.

ECHO.
ECHO [2/5] Checking code style with Flake8 (logging to %LOGFILE%)...
ECHO [FLAKE8 START] >> %LOGFILE%
flake8 src/ tests/ >> %LOGFILE% 2>&1
SET FLAKE8_ERRORLEVEL=%ERRORLEVEL%
ECHO [FLAKE8 END - Exit Code: %FLAKE8_ERRORLEVEL%] >> %LOGFILE%
ECHO. >> %LOGFILE%

IF %FLAKE8_ERRORLEVEL% NEQ 0 (
    ECHO ERROR: Flake8 found style issues.
    ECHO        Please check the details above and in %LOGFILE%.
    GOTO :flake8_error
)
ECHO      Flake8 checks passed.

ECHO.
ECHO [3/5] Formatting code with Black (logging to %LOGFILE%)...
ECHO [BLACK START] >> %LOGFILE%
black src/ tests/ >> %LOGFILE% 2>&1
SET BLACK_ERRORLEVEL=%ERRORLEVEL%
ECHO [BLACK END - Exit Code: %BLACK_ERRORLEVEL%] >> %LOGFILE%
ECHO. >> %LOGFILE%

IF %BLACK_ERRORLEVEL% NEQ 0 (
    ECHO ERROR: Black encountered an error during formatting.
    ECHO        Check the output above and in %LOGFILE%.
    GOTO :black_error
)
ECHO      Black formatting complete/verified.

ECHO.
ECHO [4/5] Building SentinelPC executable (logging to %LOGFILE%)...
ECHO [BUILD START] >> %LOGFILE%
python scripts/build_unified.py >> %LOGFILE% 2>&1
SET BUILD_ERRORLEVEL=%ERRORLEVEL%
ECHO [BUILD END - Exit Code: %BUILD_ERRORLEVEL%] >> %LOGFILE%
ECHO. >> %LOGFILE%

IF %BUILD_ERRORLEVEL% NEQ 0 (
    ECHO #############################################################
    ECHO ## CRITICAL ERROR: Build script failed!                    ##
    ECHO ## Cannot proceed to run the application.                ##
    ECHO ## Check the detailed build output in %LOGFILE%.         ##
    ECHO #############################################################
    GOTO :build_error
)
ECHO      Build successful. Executable should be in .\dist\

ECHO.
ECHO [5/5] Running the built SentinelPC executable...
ECHO ==================================================
ECHO [RUN START] >> %LOGFILE%
.\dist\SentinelPC.exe
SET RUN_ERRORLEVEL=%ERRORLEVEL%
ECHO [RUN END - Exit Code: %RUN_ERRORLEVEL%] >> %LOGFILE%
ECHO. >> %LOGFILE%

IF %RUN_ERRORLEVEL% NEQ 0 (
    ECHO WARNING: SentinelPC.exe exited with a non-zero status (%RUN_ERRORLEVEL%).
    ECHO          Check the application's own logs or console output if applicable.
    ECHO          Details might also be in %LOGFILE% if the crash produced stderr output.
    REM Decide if this is an error for the script - currently just a warning
)
ECHO ==================================================
ECHO      SentinelPC execution finished.

ECHO.
ECHO Task runner completed successfully. See %LOGFILE% for details.
GOTO :end

:flake8_error
ECHO Task runner stopped due to Flake8 errors.
GOTO :common_error_exit

:black_error
ECHO Task runner stopped due to Black formatting errors.
GOTO :common_error_exit

:build_error
ECHO Task runner stopped due to a CRITICAL build failure.
GOTO :common_error_exit

:common_error_exit
ECHO.
ECHO Please review the errors and check %LOGFILE% for full details.
PAUSE
EXIT /B 1

:end
ENDLOCAL
EXIT /B 0
