@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

:: ####################################
:: SentinelPC X WESCORE | Dev Task Runner
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
:: Runs common development tasks in sequence with logging and improved error handling:
:: --- Start of Script ---

:: Write the requested header message and initial log info (overwrites existing log)
(
  ECHO ==========================================================
  ECHO 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐟𝐨𝐫 𝐒𝐲𝐬𝐭𝐞𝐦𝐚𝐭𝐢𝐜 𝐈𝐦𝐩𝐥𝐞𝐦𝐞𝐧𝐭𝐚𝐭𝐢𝐨𝐧 𝐨𝐟 𝐈𝐦𝐩𝐫𝐨𝐯𝐞𝐦𝐞𝐧𝐭𝐬 𝐚𝐧𝐝 𝐅𝐢𝐱𝐞𝐬
  ECHO ==========================================================
  ECHO 𝗣𝗼𝘄𝗲𝗿𝗲𝗱 𝗯𝘆: 𝗦𝗲𝗻𝘁𝗶𝗻𝗲𝗹𝗣𝗖 𝗫 𝗪𝗘𝗦𝗖𝗢𝗥𝗘^|𝗗𝗲𝘃𝗲𝗹𝗼𝗽𝗺𝗲𝗻𝘁 𝗧𝗮𝘀𝗸 𝗥𝘂𝗻𝗻𝗲𝗿
  ECHO.
  ECHO Objective:
  ECHO I need your assistance in implementing improvements and fixes systematically while ensuring that the existing functionality remains intact.
  ECHO.
  ECHO Details:
  ECHO 1. Log File: Please refer to the full log trace provided in `run_tasks.log` for any relevant information.
  ECHO 2. Command Used: The command executed was `.\run_tasks.bat`.
  ECHO.
  ECHO Tasks:
  ECHO 1. Review Logs: Analyze the `run_tasks.log` file to identify any errors, warnings, or areas that need improvement.
  ECHO 2. Implement Fixes: Address the identified issues systematically, ensuring that each fix is thoroughly tested.
  ECHO 3. Maintain Functionality: Ensure that all existing functionality remains operational and unaffected by the changes.
  ECHO 4. Documentation: Document all changes made, including the rationale behind each fix and any testing procedures used.
  ECHO.
  ECHO Expected Outcome:
  ECHO - A stable system with improved performance and fixed issues.
  ECHO - Detailed documentation of all changes and testing results.
  ECHO.
  ECHO ========================================
  ECHO Starting Task Runner Log
  ECHO Timestamp: %DATE% %TIME%
  ECHO ========================================
  ECHO.
) > %LOGFILE%

:: --- End of Header Modification ---

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
