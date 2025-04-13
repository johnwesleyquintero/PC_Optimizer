# SENTINEL PC ROADMAP

## Core Goals

1.  **Consolidate into `SentinelPC`:** Merge existing functionalities (CLI, GUI, Core) into a single, unified application named `SentinelPC`. This involves architectural changes, renaming, and updating entry points/build processes.
    - [x] Verified config_manager.py and config_manager_v2.py are identical
    - [x] Removed redundant config_manager_v2.py
    - [x] Consolidated performance_optimizer_v2.py into performance_optimizer.py
    - [x] Verified sentinel_cli.py and sentinel_gui.py are properly structured
    - [x] Removed pc_optimizer_cli_v2.py and pc_optimizer_gui_v2.py
    - [x] Update import statements in all files to use new names
    - [x] Update build scripts to use consolidated files
    - [x] Test consolidated application functionality
2.  **Implement Semantic Versioning:** Adopt SemVer (e.g., `v1.0.0`) across the project for clear version tracking, remove informal version suffixes (like `_v2`) from filenames, and use Git tags.

---

## Completed

*   [x] Create a virtual environment
*   [x] Install the required packages
*   [x] Create a GitHub repository
*   [x] Create a README.md file (Initial version)
*   [x] Consolidate configuration management (`config_manager_v2.py`)
*   [x] Add initial logging to `config_manager_v2.py`
*   [x] Add improved error handling to `performance_optimizer_v2.py` (`clean_temp_files`)
*   [x] Set up basic unit testing framework (e.g., `pytest` installed, initial structure maybe present - *Verify exact status*)
*   [x] Define SentinelPC architecture in ARCHITECTURE.md

---

## Phase 1: Foundation & Consolidation (Immediate Priorities)

*These tasks focus on establishing the new `SentinelPC` structure and core improvements.*

### Project Structure & Naming
*   [x] **Define `SentinelPC` Architecture:** Plan how CLI, GUI, and Core components will integrate within the single `SentinelPC` application structure. (Medium, Design/Docs)
*   [x] **Implement Semantic Versioning:**
    *   [x] Adopt SemVer (`v1.0.0`). (Small)
    *   [x] Remove `_v2` suffixes from all relevant filenames (e.g., `pc_optimizer_cli.py`, `config_manager.py`). (Medium, Multiple files)
    *   [x] Establish process for version bumping (e.g., manual, `bump2version`) and Git tagging. (Small)
*   [x] **Rename & Reorganize:** Rename folders/files/modules to reflect the `SentinelPC` name and the defined architecture. (Medium, Multiple files)
*   [x] **Update Entry Points:** Modify/Create main script(s) for running `SentinelPC` (handling CLI vs GUI modes). (Medium, `src/`)
*   [x] **Update Build Process:** Modify `build.bat` and `.spec` files to build the consolidated `SentinelPC` application (CLI/GUI variants if needed, or a single entry point). (Medium, `scripts/`, `spec/`)

### Core Improvements & Stability
*   [x] **Verify/Create `LICENSE` file:** Ensure a proper `LICENSE` file exists. (Small)
*   [x] **Create `CONTRIBUTING.md`:** Define contribution guidelines. (Small)
*   [x] **Enhance Dependency Management:**
    *   [x] Pin dependencies in `requirements.txt` (`pip freeze > requirements.txt`). (Small)
    *   [x] Organized dependencies into clear categories (Core, Web Framework, UI Components, etc.)
    *   [x] Moved development tools to requirements-dev.txt
*   [x] **Implement Centralized Logging:** Set up project-wide logging using Python's `logging` module, configurable via `config.ini`.
    *   [x] Updated core modules to use centralized logging
    *   [x] Ensured consistent log formatting and handling
    *   [x] Integrated with config.ini for configurable logging settings
*   [ ] **Refactor `environment_manager.py`:** Update to use `EnvironmentConfig` from the consolidated config manager. (Medium, `src/core/environment_manager.py` - *path may change after rename*)
*   [ ] **Add Initial Tests for Core Modules:**
    *   [ ] Add basic unit tests for `config_manager.py`. (Small, `tests/`)
    *   [ ] Add basic unit tests for `performance_optimizer.py`. (Small, `tests/`)
    *   [ ] Add logs to `config_manager.py` (track loading, saving, validation). (Small, `src/core/config_manager.py`)
    *   [ ] Add logs to `performance_optimizer.py` (track function calls, parameters, results). (Small, `src/core/performance_optimizer.py`)
*   [ ] **Setup Basic CI Pipeline:** Implement GitHub Actions (or similar) to run linters (`flake8`), formatters (`black`), and initial unit tests on push/PR. (Medium)

---

## Phase 2: Refinement & Feature Development

*Build upon the consolidated foundation.*

### Code Quality & Refactoring
*   [ ] **Review and Refactor `performance_optimizer.py`:** Conduct a thorough review and refactor for clarity, efficiency, and adherence to the new architecture. (Medium, `src/core/performance_optimizer.py`)
*   [ ] **Enforce Code Style:** Run `flake8` and `black` across the codebase and fix violations. Integrate into CI. (Small, Multiple files)
*   [ ] **Improve Error Handling:** Define custom exceptions, catch specific errors, provide user-friendly GUI error messages. (Medium, Multiple files)

### Testing Expansion
*   [ ] **Increase Test Coverage:** Write more unit tests for core logic, aiming for measurable coverage. (Medium, `tests/`)
*   [ ] **Set up Test Coverage Reporting:** Integrate `coverage.py` into the test suite and CI. (Small, `tests/`, CI config)
*   [ ] **Add Integration Tests:** Develop tests for CLI and GUI interactions (basic workflows). (Medium, `tests/`)

### Documentation
*   [ ] **Update `README.md`:** Reflect the consolidated `SentinelPC` application, new structure, and usage. (Small, `README.md`)
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

\---

## Codebase Improvements (New Tasks)

### High Priority

*   [ ] **Implement GUI Placeholder Functions:** Implement the actual functionality for `check_disk_usage`, `manage_startup_programs`, `optimize_power_settings`, and `run_disk_cleanup` in `src/gui/pc_optimizer_gui.py`.
*   [ ] **Prevent GUI Freezing:** Use threading or asyncio to run the optimizations in a separate thread or coroutine in `src/gui/pc_optimizer_gui.py` to prevent the GUI from freezing.

### Medium Priority

*   [ ] **Improve GUI Theme Application:** Implement a more comprehensive theme system in `src/gui/pc_optimizer_gui.py` that allows for customization of all UI elements. Implement actual color adjustment logic for hover effects.
*   [ ] **Add GUI Error Handling:** Add error handling to the optimization functions in `src/gui/pc_optimizer_gui.py` to catch potential exceptions and display user-friendly error messages in the GUI.
*   [ ] **Use `shutil.disk_usage` in `clean_temp_files`:** Use `shutil.disk_usage` to check disk space before cleaning temp files in `src/core/performance_optimizer.py`.
*   [ ] **Add Specific Error Handling in `clean_temp_files`:** Catch specific exceptions like `PermissionError` and handle them accordingly in `src/core/performance_optimizer.py`.
*   [ ] **Validate Configuration Values:** Validate the configuration values loaded from the `config.ini` file in `src/core/environment_manager.py` to ensure they are within acceptable ranges.
*   [ ] **Handle Missing Configuration Values:** Implement a mechanism to handle missing configuration values in `src/core/environment_manager.py`.
*   [ ] **Implement Windows Theme Performance Adjustments:** Implement actual performance adjustments for dark mode on Windows in `src/core/performance_optimizer.py`.
*   [ ] **Log to GUI:** Implement logging to the `log_text` widget in the GUI in `src/gui/pc_optimizer_gui.py`.

### Low Priority

*   [ ] **Consider More Robust Temp File Cleaning:** Consider using a more targeted approach for temporary file cleaning in `src/core/performance_optimizer.py`.
*   [ ] **Refactor `adjust_memory_usage`:** Refactor the `adjust_memory_usage` function in `src/core/performance_optimizer.py` to use a more centralized configuration management approach.
*   [ ] **Consider More Robust Directory Creation:** Ensure the existence of other required directories in `src/core/environment_manager.py`.

=======
*   [ ] **Monitoring & Auto-Updates:** Add health checks, performance monitoring, update mechanisms. (Medium)
