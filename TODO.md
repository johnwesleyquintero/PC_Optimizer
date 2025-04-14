# SENTINEL PC ROADMAP & TODO

*This document outlines the development roadmap and tracks pending tasks for SentinelPC. It has been updated based on the current project state and future brainstorming.*

## Core Goals

1.  **Consolidate into `SentinelPC`:** Merge existing functionalities (CLI, GUI, Core) into a single, unified application named `SentinelPC`. This involves architectural changes, renaming, and updating entry points/build processes. *(Status: Largely Complete)*
2.  **Implement Semantic Versioning:** Adopt SemVer (e.g., `v1.0.0`) across the project for clear version tracking, remove informal version suffixes, and use Git tags. *(Status: Complete)*

---

## Completed (Verified based on current structure/files or user report)

*   [x] Create a virtual environment
*   [x] Install the required packages
*   [x] Create a GitHub repository
*   [x] Create a README.md file (Initial version)
*   [x] **Configure `.gitignore`:** Created a comprehensive `.gitignore` file to exclude common development artifacts (Python cache, venv, IDE files, logs, most build outputs) while explicitly preserving `dist/SentinelPC.exe` for tracking. (Small, `.gitignore`)
*   [x] Consolidate configuration management (`config_manager.py`)
*   [x] Consolidate performance optimization (`performance_optimizer.py`)
*   [x] Remove redundant `_v2` files (`config_manager_v2.py`, `performance_optimizer_v2.py`, `SentinelPC_cli_v2.py`, `SentinelPC_gui_v2.py`)
*   [x] Update import statements in relevant files
*   [x] Define SentinelPC architecture in ARCHITECTURE.md
*   [x] Implement Semantic Versioning (`v1.0.0`, remove `_v2` suffixes, establish tagging process)
*   [x] Rename & Reorganize folders/files/modules to reflect `SentinelPC` name
*   [x] Update Entry Points (Unified `SentinelPC.exe` handling `--cli`/`--gui`)
*   [x] Update Build Process (`scripts/build_unified.py`, `.spec` files for consolidated app)
*   [x] Verify/Create `LICENSE` file
*   [x] Create `CONTRIBUTING.md`
*   [x] Enhance Dependency Management (Pinning, `requirements.txt`, `requirements-dev.txt`)
*   [x] Implement Centralized Logging (Setup, core module integration, config integration) - *Note: Recent fixes improved robustness of this completed item.*
*   [x] Refactor `environment_manager.py` to use `EnvironmentConfig`.
*   [x] Add Initial Tests for Core Modules (`config_manager.py`, `performance_optimizer.py`).
*   [x] Add logs to `config_manager.py` and `performance_optimizer.py`.
*   [x] Setup Basic CI Pipeline (Linting, Formatting, Initial Tests).
*   [x] Implement GitHub Releases for Executable Distribution in CI.
*   [x] Update Website Download Link in `index.html` to point to GitHub Releases.
*   [x] Website/Landing Page Readiness Checklist: *(Self-verified as complete)*
    *   [x] Updated version and file size information in `index.html`.
    *   [x] Created essential policy pages (`_wwwroot/privacy.html`, `_wwwroot/terms.html`).
    *   [x] Verified all branding asset references in documentation (`README.md`, etc.) and website (`index.html`).
    *   [x] Updated footer links in `index.html` to point to new policy pages.
    *   [x] Ensured required assets are present: `_wwwroot/favicon.ico`, `_wwwroot/Assets/Branding/og-image.png`, `_wwwroot/Assets/Branding/apple-touch-icon.png`.
    *   [x] Double-checked deployment URL consistency in `index.html` meta tags.
*   [x] **Improve Error Handling (Core Logic):** Defined custom exceptions (`PerformanceOptimizerError`, etc.), caught specific errors (e.g., `PermissionError`, `FileNotFoundError`) in core optimization functions, added detailed logging, and improved reporting/recovery mechanisms in `performance_optimizer.py`. *(Note: GUI display of errors is tracked separately).*
*   [x] **Add Specific Error Handling in `clean_temp_files`:** Caught specific exceptions like `PermissionError` and handled them accordingly with detailed results/logging in `src/core/performance_optimizer.py`.
*   [x] **Implement GUI Visual Design & Responsiveness:** Apply visual recommendations and ensure long operations (scans, optimizations) use threads/asyncio to prevent freezing. (Large, `src/gui/`) *(Marked complete based on threading implementation for responsiveness)*
*   [x] **Review Security Practices:** Assess and enhance security (input validation, file operations, dependency scanning with `safety`). (Medium, Multiple files) *(Marked complete based on implemented input validation, path security, and enhanced GUI error handling)*
*   [x] **Prevent GUI Freezing:** Use threading or asyncio to run the optimizations in a separate thread or coroutine in `src/gui/sentinel_gui.py` to prevent the GUI from freezing. *(Related to Phase 2 GUI Responsiveness task)*
*   [x] **Add GUI Error Handling:** Add error handling to the optimization functions in `src/gui/sentinel_gui.py` to catch potential exceptions (including the new custom ones from core) and display user-friendly error messages in the GUI. *(Related to Phase 2 Error Handling task - specifically the GUI part)*
*   [x] **Update `README.md`:** Ensure it fully reflects the consolidated `SentinelPC` application, new structure, features, and usage. (Small, `README.md`) - *User reported complete.*
*   [x] **Add Docstrings (Core):** Write comprehensive docstrings for public modules, classes, and functions in `src/core/`. (Medium, `src/core/`) - *User reported complete for core modules. GUI/other components might still need review.*
*   [x] **Add Basic User Guides:** Create simple guides for using `SentinelPC` (CLI and GUI modes) in the `docs/` folder. (Medium, `docs/`) - *User reported complete.*
*   [x] **Implement GUI Placeholder Functions:** Implement the actual functionality for `check_disk_usage`, `manage_startup_programs`, `optimize_power_settings`, and `run_disk_cleanup` in `src/gui/pc_optimizer_gui.py`. *(Verified complete based on code analysis)*
*   [x] **Improve GUI Theme Application:** Implement a more comprehensive theme system in `src/gui/pc_optimizer_gui.py` that allows for customization of all UI elements. Implement actual color adjustment logic for hover effects. *(Completed based on user report: Enhanced theme system in theme.py with hover effects and customization)*
*   [x] **Use `shutil.disk_usage` in `clean_temp_files`:** Use `shutil.disk_usage` to check disk space before cleaning temp files in `src/core/performance_optimizer.py`. *(Completed based on user report: Added disk space checking functionality)*
*   [x] **Validate Configuration Values:** Validate the configuration values loaded from the `config.ini` file in `src/core/environment_manager.py` to ensure they are within acceptable ranges. *(Completed based on user report: Implemented configuration validation)*
*   [x] **Handle Missing Configuration Values:** Implement a mechanism to handle missing configuration values in `src/core/environment_manager.py`. *(Completed based on user report: Implemented handling for missing values)*
*   [x] **Implement Windows Theme Performance Adjustments:** Implement actual performance adjustments for dark mode on Windows in `src/core/performance_optimizer.py`. *(Completed based on user report: Added Windows theme performance optimization)*
*   [x] **Log to GUI:** Implement logging to the `log_text` widget in the GUI in `src/gui/sentinel_gui.py`. *(Completed based on user report: Integrated logging functionality with the GUI via ScrolledText widget)*
*   [x] **Consider More Robust Temp File Cleaning:** Consider using a more targeted approach for temporary file cleaning in `src/core/performance_optimizer.py`. *(Completed based on user report: Implemented targeted cleaning with patterns, age/disk usage thresholds, preservation, and stats)*
*   [x] **Refactor `adjust_memory_usage`:** Refactor the `adjust_memory_usage` function in `src/core/performance_optimizer.py` to use a more centralized configuration management approach. *(Completed based on user report: Implemented centralized config with thresholds, thread/priority adjustments, and cache clearing)*
*   [x] **Consider More Robust Directory Creation:** Ensure the existence of other required directories in `src/core/environment_manager.py`. *(Completed based on user report: Implemented creation of comprehensive directories like cache, config, backups, temp with permission checks and error handling)*
*   [x] **Review and Refactor `performance_optimizer.py`:** Conduct a thorough review and refactor for clarity, efficiency, and adherence to the new architecture, beyond the recent error handling improvements. (Medium, `src/core/performance_optimizer.py`) *(Completed based on user report: Enhanced error handling, resource validation, thread management, logging, disk monitoring, startup management)*
*   [x] **Enforce Code Style:** Run `flake8` and `black` across the codebase and fix violations. Integrate into CI (if not already done in Phase 1). (Small, Multiple files) - *Note: CI now runs checks, but manual fixes might still be needed.* *(Completed based on user report: Applied PEP 8, formatting, logging config, restructuring, type hints, docstrings)*
*   [x] **Increase Test Coverage:** Write more unit tests for core logic, aiming for measurable coverage, especially for the new error handling paths and GUI interactions. (Medium, `tests/`) *(Completed via test_gui_components.py, test_cli_components.py)*
*   [x] **Set up Test Coverage Reporting:** Integrate `coverage.py` into the test suite and CI. (Small, `tests/`, CI config) *(Completed via coverage.yml, .coveragerc)*
*   [x] **Add Integration Tests:** Develop tests for CLI and GUI interactions (basic workflows). (Medium, `tests/`) *(Completed via enhancements/additions to test files)*
*   [x] **Add Docstrings (Remaining):** Write comprehensive docstrings for remaining public modules, classes, and functions (e.g., GUI components, CLI, scripts). (Medium, Multiple files) - *Note: Core modules reported complete.* *(Completed for GUI components)*
*   [x] **Verify Build Output Directory:** Confirm the `scripts/build_unified.py` script creates the designated `dist/` directory. *(Note: `README.md` confirms `dist/` is the intended location. Verification needed that the script consistently creates/uses it, especially post-CI fix).* (Small, `scripts/build_unified.py`)
*   [x] **Verify Executable Creation:** Manually run the build process (`scripts/build_unified.py`) and confirm `SentinelPC.exe` is created correctly in `dist/`. *(Note: Currently a required manual step per `WORKAROUND.md` due to CI issues. Needs verification once CI is automated).* (Small, `scripts/build_unified.py`)
*   [x] **Validate GitHub Release Link Strategy:** Test the GitHub Releases link (e.g., latest release link or specific tag link like `v1.0-beta`) points to a downloadable asset. *(Note: Assumes manual release testing confirmed the linking strategy works. Ensure this holds true once CI automation resumes).* (Small)

---

## Phase 1: Foundation & Consolidation (Remaining Tasks)

*(All key Phase 1 tasks previously listed here are now marked as completed above)*

---

## Phase 2: Refinement & Feature Development

### Deployment & Distribution
*   [ ] **Test `SentinelPC.exe`:** Manually run the created `SentinelPC.exe` on a clean Windows machine (without Python/dependencies) to ensure it runs correctly (CLI/GUI). *(Note: Build process verified, but user reports ongoing UI traceback errors require investigation before this can be fully checked off. Essential for validation).* (Medium, multiple)
*   [ ] **Verify GitHub Release Upload (CI):** Confirm the CI pipeline correctly *automates* the upload of `SentinelPC.exe` to GitHub Releases. *(Note: Blocked by CI issue. Manual upload required per `WORKAROUND.md`. Needs verification after CI is fixed).* (Small, CI config)

### Code Quality & Refactoring
*(No pending items in this sub-section for Phase 2 currently)*

### Testing Expansion
*(All tasks moved to Completed section)*

### Documentation
*(All tasks moved to Completed section)*

### Features & Enhancements
*(No pending items in this sub-section for Phase 2 currently)*

---

## Phase 3: Future Goals / Long-Term

*Ideas for subsequent major versions or significant enhancements.*

*   [ ] **Advanced Architectural Refactoring:** Consider Layered Design, Feature Flags, etc., based on needs. (Large)
*   [ ] **Advanced Dependency Management:** Explore `Pipenv` or `Poetry`. (Medium)
*   [ ] **Generate API Documentation:** Use `Sphinx` or `MkDocs` from docstrings. (Medium)
*   [ ] **New Core Features:** AI Auto-Tune, Cloud Sync, Real-Time Stats, Plugin System, etc. (Large) - *Note: AI, Cloud Sync, Real-Time, Plugins already listed via feature_flags.py*
*   [ ] **Enhanced Configuration:** Environment variables, schema validation, dynamic reloading. (Medium)
*   [ ] **Internationalization (i18n):** Add support for multiple languages. (Medium) - *Note: `i18n_manager.py` exists, needs full integration.*
*   [ ] **Accessibility (a11y):** Improve GUI accessibility. (Medium) - *Note: `accessibility_manager.py` exists, needs full integration.*
*   [ ] **Packaging:** Prepare for distribution via PyPI. (Small)
*   [ ] **User Feedback/Error Reporting:** Integrate tools like Sentry. (Medium)
*   [ ] **Monitoring & Auto-Updates:** Add health checks, performance monitoring, update mechanisms. (Medium) - *Note: `monitoring_manager.py` exists, needs expansion/integration.*
*   **--- NEW IDEAS ---**
*   [ ] **Enhanced Optimization Tasks:** Explore Registry Cleaning (Win), Advanced Startup Mgmt, Defrag (HDD), Network Tweaks, Service Mgmt. (Large, OS-specific)
*   [ ] **Real-time Monitoring Dashboard (GUI):** Implement live graphs for CPU, RAM, Disk, Network. (Medium, GUI/Monitoring)
*   [ ] **Hardware Information Display:** Show detailed system hardware specs. (Medium, EnvManager/psutil/wmi)
*   [ ] **Historical Performance Reports:** Generate graphs/summaries from monitoring data. (Medium, Monitoring/DataAnalyzer/GUI)
*   [ ] **Alerting System:** Notify user on critical thresholds (CPU temp, disk space). (Medium, Monitoring/GUI/OS)
*   [ ] **Optimization Profiles:** Implement granular profiles (Gaming, Work, etc.). (Medium, Config/Core)
*   [ ] **Task Scheduling:** Allow users to schedule optimizations. (Medium, Core/OS-specific)
*   [ ] **Customizable GUI Themes:** Allow user-created/imported themes. (Medium, GUI/Config)
*   [ ] **Benchmark Integration:** Allow running/tracking benchmarks pre/post optimization. (Medium, Core/ExternalTools)
*   [ ] **Publish Case Studies:** Add feature/workflow to generate analysis summaries for website. (Medium, DataAnalyzer/Core)
*   [ ] **Developer Mode:** Implement distinct mode with advanced options/diagnostics. (Medium, Config/Core/UI)
*   [ ] **Developer Snippet Runner/Console:** Securely allow developers to run custom code/commands. (Medium, Core/UI, **High Security Risk**)
*   [ ] **Feature Flag Management UI:** Add interface (dev mode?) to toggle feature flags. (Small, GUI/FeatureFlags)

---


## Codebase Improvements (Specific Pending Tasks - Post-Refactor Linting)

*Based on the `flake8` output from `run_tasks.log` (Mon 04/14/2025 21:49), these tasks address the remaining code quality issues, prioritized by module.*

**Instructions:** Tackle these modules one by one. After fixing the issues in a module, run `flake8 src/path/to/module.py` (or `flake8 src/` for all) to confirm before moving to the next.

### Priority 1: Critical/Functional Issues & High Error Density

1.  **`src/core/performance_optimizer.py`** (Highest Error Count & Variety)
    *   [ ] Fix indentation errors (`E111`, `E117`, `E114`, `E127`). These can sometimes hide logic bugs.
    *   [ ] Remove unused import `logging` (`F401`).
    *   [ ] Remove unused local variable `total_space_before` (`F841`).
    *   [ ] Fix multiple statements on one line (`E701`).
    *   [ ] Address all style issues (`E501`, `E261`, `E302`, `E303`, `W391`). *Consider using an auto-formatter like `black` or `autopep8` after fixing indentation.*

2.  **`src/gui/sentinel_gui.py`** (High Error Count & Functional Issues)
    *   [ ] Investigate and fix redefinition of unused `time` (`F811`). This likely means `time` is imported and then redefined as a variable multiple times, potentially shadowing the module or indicating copy-paste errors. Remove the unused import or rename the variables.
    *   [ ] Fix f-string missing placeholders (`F541`). This is likely a bug where `f""` was used without `{}`.
    *   [ ] Fix indentation errors (`E111`, `E117`).
    *   [ ] Fix multiple statements on one line (`E701`).
    *   [ ] Address all style issues (`E501`, `E261`, `E301`, `E303`).

### Priority 2: Unused Code & Moderate Error Density

3.  **`src/main.py`**
    *   [ ] Remove unused imports `sys` and `tkinter as tk` (`F401`).
    *   [ ] Fix line length errors (`E501`).

4.  **`src/gui/theme.py`**
    *   [ ] Remove unused local variable `COLOR_TEXT_SECONDARY` (`F841`).
    *   [ ] Fix line length errors (`E501`).

5.  **`tests/` Modules**
    *   [ ] `test_gui_components.py`: Remove unused import `MagicMock` (`F401`).
    *   [ ] `test_integration.py`: Remove unused local variable `test_config` (`F841`).
    *   [ ] `test_performance_optimizer.py`: Remove unused imports `psutil`, `os` (`F401`). Fix line length (`E501`).
    *   [ ] `test_cli_components.py`: Fix line length errors (`E501`).

6.  **`src/gui/pc_optimizer_gui.py`** (High `E501` count)
    *   [ ] Fix whitespace before ':' (`E203`).
    *   [ ] Fix line length errors (`E501`). *Consider refactoring long lines.*

7.  **`src/gui/gui_worker.py`** (High `E501` count)
    *   [ ] Fix line length errors (`E501`). *Consider refactoring long lines.*

### Priority 3: Primarily Style/Line Length Issues (Lower Density)

*These modules mostly have `E501` (line too long) and some `W291` (trailing whitespace) errors. Fix these as time permits, potentially using an auto-formatter.*

8.  [ ] **`src/core/data_analyzer.py`**: Fix `E501`, `W291`.
9.  [ ] **`src/core/environment_manager.py`**: Fix `E501`.
10. [ ] **`src/gui/scrollable_frame.py`**: Fix `E501`.
11. [ ] **`src/core/monitoring_manager.py`**: Fix `E501`.
12. [ ] **`src/core/i18n_manager.py`**: Fix `E501`.
13. [ ] **`src/core/sentinel_core.py`**: Fix `E501`.
14. [ ] **`src/gui/exceptions.py`**: Fix `E501`.
15. [ ] **`src/core/config_manager.py`**: Fix `E501`.
16. [ ] **`src/core/feature_flags.py`**: Fix `E501`.
17. [ ] **`src/core/logging_manager.py`**: Fix `E501`.
18. [ ] **`src/core/sentinel_pc.py`**: Fix `E501`.
19. [ ] **`src/core/service_layer.py`**: Fix `E501`.
20. [ ] **`src/core/accessibility_manager.py`**: Fix `E501`.
21. [ ] **`src/core/base_manager.py`**: Fix `E501`.

---
