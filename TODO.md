# SENTINEL PC ROADMAP & TODO

*This document outlines the development roadmap and tracks pending tasks for SentinelPC. It has been updated based on the current project state.*

## Core Goals

1.  **Consolidate into `SentinelPC`:** Merge existing functionalities (CLI, GUI, Core) into a single, unified application named `SentinelPC`. This involves architectural changes, renaming, and updating entry points/build processes. *(Status: Largely Complete)*
2.  **Implement Semantic Versioning:** Adopt SemVer (e.g., `v1.0.0`) across the project for clear version tracking, remove informal version suffixes, and use Git tags. *(Status: Complete)*

---

## Completed (Verified based on current structure/files)

*   [x] Create a virtual environment
*   [x] Install the required packages
*   [x] Create a GitHub repository
*   [x] Create a README.md file (Initial version)
*   [x] Consolidate configuration management (`config_manager.py`)
*   [x] Consolidate performance optimization (`performance_optimizer.py`)
*   [x] Remove redundant `_v2` files (`config_manager_v2.py`, `performance_optimizer_v2.py`, `pc_optimizer_cli_v2.py`, `pc_optimizer_gui_v2.py`)
*   [x] Update import statements in relevant files
*   [x] Define SentinelPC architecture in ARCHITECTURE.md
*   [x] Implement Semantic Versioning (`v1.0.0`, remove `_v2` suffixes, establish tagging process)
*   [x] Rename & Reorganize folders/files/modules to reflect `SentinelPC` name
*   [x] Update Entry Points (Unified `SentinelPC.exe` handling `--cli`/`--gui`)
*   [x] Update Build Process (`build_unified.py`, `.spec` files for consolidated app)
*   [x] Verify/Create `LICENSE` file
*   [x] Create `CONTRIBUTING.md`
*   [x] Enhance Dependency Management (Pinning, `requirements.txt`, `requirements-dev.txt`)
*   [x] Implement Centralized Logging (Setup, core module integration, config integration)
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
    *   [x] Ensured required assets are present: `_wwwroot/favicon.ico`, `wwwroot/Assets/Branding/og-image.png`, `wwwroot/Assets/Branding/apple-touch-icon.png`.
    *   [x] Double-checked deployment URL consistency in `index.html` meta tags.

---

## Phase 1: Foundation & Consolidation (Remaining Tasks)

*(All key Phase 1 tasks previously listed here are now marked as completed above)*

---

## Phase 2: Refinement & Feature Development

### Deployment & Distribution
*   **Executable Distribution Verification:**
    *   [ ] **Verify Build Output Directory:** Confirm the `build_unified.py` script creates a designated directory (e.g., `dist/`) for the executable. If not, update the script to create this directory. (Small, `build_unified.py`)
    *   [ ] **Verify Executable Creation:** Manually run the build process (`build_unified.py`) and confirm that the `SentinelPC.exe` is created correctly in the output directory. (Small, `build_unified.py`)
    *   [ ] **Test `SentinelPC.exe`:** Manually run the created `SentinelPC.exe` on a clean Windows machine (without Python or dependencies) to ensure it runs correctly and the CLI/GUI entry points work. (Medium, multiple)
    *   [ ] **Verify GitHub Release Upload:** Confirm that the CI pipeline correctly uploads `SentinelPC.exe` to GitHub Releases on each release. Double check if the correct files are attached to the release. (Small, CI config)
    *   [ ] **Validate GitHub Release Link:** Test the `https://github.com/johnwesleyquintero/SentinelPC/releases/latest/download/SentinelPC.exe` link after a CI release to ensure it downloads the correct file. (Small)

### Code Quality & Refactoring
*   [ ] **Review and Refactor `performance_optimizer.py`:** Conduct a thorough review and refactor for clarity, efficiency, and adherence to the new architecture. (Medium, `src/core/performance_optimizer.py`)
*   [ ] **Enforce Code Style:** Run `flake8` and `black` across the codebase and fix violations. Integrate into CI (if not already done in Phase 1). (Small, Multiple files) - *Note: CI now runs checks, but manual fixes might still be needed.*
*   [ ] **Improve Error Handling:** Define custom exceptions, catch specific errors, provide user-friendly GUI error messages. (Medium, Multiple files)

### Testing Expansion
*   [ ] **Increase Test Coverage:** Write more unit tests for core logic, aiming for measurable coverage. (Medium, `tests/`)
*   [ ] **Set up Test Coverage Reporting:** Integrate `coverage.py` into the test suite and CI. (Small, `tests/`, CI config)
*   [ ] **Add Integration Tests:** Develop tests for CLI and GUI interactions (basic workflows). (Medium, `tests/`)

### Documentation
*   [ ] **Update `README.md`:** Ensure it fully reflects the consolidated `SentinelPC` application, new structure, features, and usage. (Small, `README.md`) - *Review needed, but largely up-to-date.*
*   [ ] **Add Docstrings:** Write comprehensive docstrings for public modules, classes, and functions. (Medium, Multiple files)
*   [ ] **Add Basic User Guides:** Create simple guides for using `SentinelPC` (CLI and GUI modes) in the `docs/` folder. (Medium, `docs/`)

### Features & Enhancements
*   [ ] **Implement GUI Visual Design & Responsiveness:** Apply visual recommendations and ensure long operations (scans, optimizations) use threads/asyncio to prevent freezing. (Large, `src/gui/`)
*   [ ] **Review Security Practices:** Assess and enhance security (input validation, file operations, dependency scanning with `safety`). (Medium, Multiple files)

---

## Phase 3: Future Goals / Long-Term

*Ideas for subsequent major versions or significant enhancements.*

*   [ ] **Advanced Architectural Refactoring:** Consider Layered Design, Feature Flags, etc., based on needs. (Large)
*   [ ] **Advanced Dependency Management:** Explore `Pipenv` or `Poetry`. (Medium)
*   [ ] **Generate API Documentation:** Use `Sphinx` or `MkDocs` from docstrings. (Medium)
*   [ ] **New Core Features:** AI Auto-Tune, Cloud Sync, Real-Time Stats, Plugin System, etc. (Large)
*   [ ] **Enhanced Configuration:** Environment variables, schema validation, dynamic reloading. (Medium)
*   [ ] **Internationalization (i18n):** Add support for multiple languages. (Medium)
*   [ ] **Accessibility (a11y):** Improve GUI accessibility. (Medium)
*   [ ] **Packaging:** Prepare for distribution via PyPI. (Small)
*   [ ] **User Feedback/Error Reporting:** Integrate tools like Sentry. (Medium)
*   [ ] **Monitoring & Auto-Updates:** Add health checks, performance monitoring, update mechanisms. (Medium)

---

## Codebase Improvements (Specific Pending Tasks)

*These are more granular tasks identified for improvement.*

### High Priority
*   [ ] **Implement GUI Placeholder Functions:** Implement the actual functionality for `check_disk_usage`, `manage_startup_programs`, `optimize_power_settings`, and `run_disk_cleanup` in `src/gui/sentinel_gui.py`. *(Note: filename might be different after rename)*
*   [ ] **Prevent GUI Freezing:** Use threading or asyncio to run the optimizations in a separate thread or coroutine in `src/gui/sentinel_gui.py` to prevent the GUI from freezing. *(Related to Phase 2 GUI Responsiveness task)*

### Medium Priority
*   [ ] **Improve GUI Theme Application:** Implement a more comprehensive theme system in `src/gui/sentinel_gui.py` that allows for customization of all UI elements. Implement actual color adjustment logic for hover effects.
*   [ ] **Add GUI Error Handling:** Add error handling to the optimization functions in `src/gui/sentinel_gui.py` to catch potential exceptions and display user-friendly error messages in the GUI. *(Related to Phase 2 Error Handling task)*
*   [ ] **Use `shutil.disk_usage` in `clean_temp_files`:** Use `shutil.disk_usage` to check disk space before cleaning temp files in `src/core/performance_optimizer.py`.
*   [ ] **Add Specific Error Handling in `clean_temp_files`:** Catch specific exceptions like `PermissionError` and handle them accordingly in `src/core/performance_optimizer.py`. *(Related to Phase 2 Error Handling task)*
*   [ ] **Validate Configuration Values:** Validate the configuration values loaded from the `config.ini` file in `src/core/environment_manager.py` to ensure they are within acceptable ranges.
*   [ ] **Handle Missing Configuration Values:** Implement a mechanism to handle missing configuration values in `src/core/environment_manager.py`.
*   [ ] **Implement Windows Theme Performance Adjustments:** Implement actual performance adjustments for dark mode on Windows in `src/core/performance_optimizer.py`.
*   [ ] **Log to GUI:** Implement logging to the `log_text` widget in the GUI in `src/gui/sentinel_gui.py`.

### Low Priority
*   [ ] **Consider More Robust Temp File Cleaning:** Consider using a more targeted approach for temporary file cleaning in `src/core/performance_optimizer.py`.
*   [ ] **Refactor `adjust_memory_usage`:** Refactor the `adjust_memory_usage` function in `src/core/performance_optimizer.py` to use a more centralized configuration management approach.
*   [ ] **Consider More Robust Directory Creation:** Ensure the existence of other required directories in `src/core/environment_manager.py`.
