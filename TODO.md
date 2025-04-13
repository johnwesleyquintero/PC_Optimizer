# SENTINEL PC ROADMAP

## Goal 
- [ ] Consolidate configuration management and functionality into one app called `SentinelPC`. This will simplify the user experience and make it easier to manage configurations and performance settings.
- [ ] Implement Semantic Versioning (e.g., v1.0 e.

## Completed
- [x] Create a virtual environment
- [x] Install the required packages
- [x] Create a GitHub repository
- [x] Create a README.md file
- [x] Create a LICENSE file (*Verify this is accurate, README mentions 'to be created'*)
- [x] Consolidate configuration management and provide visual design recommendations.
- [x] Implement unit tests for core logic (`src/core/`) using `pytest` or `unittest`.

## Immediate Tasks / Next Steps (Based on Feedback & Current TODOs)

### Refactoring & Code Quality
- [ ] Refactor `environment_manager.py` to use `EnvironmentConfig` from `src.core.config_manager_v2`. (Medium, `src/environment_manager.py`)
- [ ] Review and refactor `performance_optimizer_v2.py`. (Medium, `src/performance_optimizer_v2.py`)
- [ ] Implement Semantic Versioning (e.g., v1.0.0) and remove version suffixes from filenames (`_v2`). (Small, Multiple files)
- [ ] Enforce code style (PEP 8) using linters (e.g., `flake8`) and formatters (e.g., `black`). (Small, Multiple files)
- [ ] Improve error handling (define custom exceptions, catch specific errors, user-friendly GUI messages). (Medium, Multiple files)

### Testing
- [ ] Add integration tests for CLI/GUI interactions. (Medium, `tests/`)
- [ ] Set up test coverage reporting (e.g., using `coverage.py`). (Small, `tests/`)
- [ ] Add logs to `performance_optimizer_v2.py` to track function calls, input parameters, and return values. (Small, `src/performance_optimizer_v2.py`)
- [ ] Add tests for `config_manager_v2.py`. Add logs to `config_manager_v2.py` to track configuration loading, saving, and validation. (Small, `src/config_manager_v2.py`, `tests/test_config_manager_v2.py`)

### Documentation & Dependencies
- [ ] Create `CONTRIBUTING.md`. (Small)
- [ ] Add comprehensive docstrings to public modules, classes, and functions. (Medium, Multiple files)
- [ ] Add basic user guides to `docs/` folder (for CLI and GUI). (Medium, `docs/`)
- [ ] Pin dependencies in `requirements.txt` (`pip freeze > requirements.txt`). (Small)
- [ ] Create `requirements-dev.txt` for development-specific tools (testing, linting). (Small)

### Features & Enhancements
- [ ] Implement visual design recommendations & improve GUI responsiveness (e.g., async tasks for long operations). (Large, `src/gui/`)
- [ ] Implement centralized logging using Python's `logging` module (configurable via `config.ini`). (Medium, Multiple files)
- [ ] Review and enhance security practices (input validation, dependency scanning with e.g., `safety`). (Medium, Multiple files)

### Build & Deployment
- [ ] Set up a basic CI (Continuous Integration) pipeline (e.g., GitHub Actions) for automated tests and linting. (Medium)

## Future Goals / Long-Term

- [ ] Plan/Implement architectural refactoring (Layered Design, Feature Flags, Unified Entry Point). (Large)
- [ ] Explore advanced dependency management (e.g., `Pipenv`, `Poetry`). (Medium)
- [ ] Generate formal API documentation (e.g., using `Sphinx` or `MkDocs`). (Medium)
- [ ] Implement new core features (e.g., AI Auto-Tune, Cloud Sync, Real-Time Stats, Plugin System). (Large)
- [ ] Enhance configuration management (e.g., environment variables, validation, dynamic reloading). (Medium)
- [ ] Add Internationalization (i18n) support. (Medium)
- [ ] Improve Accessibility (a11y) for the GUI. (Medium)
- [ ] Consider packaging for PyPI. (Small)
- [ ] Implement user feedback mechanism and error reporting (e.g., Sentry). (Medium)
- [ ] Add monitoring, health checks, and potentially auto-updates. (Medium)
