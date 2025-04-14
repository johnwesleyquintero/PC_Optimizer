# TODO & Identified Issues

This document tracks identified issues, bugs, and areas for improvement based on code analysis and testing logs.

**Source Log:** `run_tasks.log` (Timestamp: Mon 04/14/2025 18:16:37.32)

## Command Used

`.\run_tasks.bat`

## Priority: Critical 🚨 (Must Fix - Code Execution/Syntax Errors)

-   [x] **Syntax Error:** Fix `IndentationError: unexpected indent` in `src/gui/sentinel_gui.py` at line `867`.
    -   `src/gui/sentinel_gui.py:867:13: E999 IndentationError: unexpected indent`
-   [x] **Name Error:** Resolve `undefined name 'SentinelCLI'` in `src/main.py` at line `76`.
    -   `src/main.py:76:19: F821 undefined name 'SentinelCLI'`

## Priority: High 🔥 (Likely Bugs / Major Refactoring Needed)

-   [ ] **Code Redefinition:** Investigate and resolve multiple function redefinitions (`F811`) in `src/core/performance_optimizer.py`. This suggests copy-paste errors or incorrect code structure. Affected functions include:
    -   `_adjust_windows_theme_performance` (lines 458 -> 973 -> 1548)
    -   `get_disk_usage` (lines 462 -> 977 -> 1552)
    -   `manage_startup_programs` (lines 540 -> 1055 -> 1630)
    -   `_manage_windows_startup` (lines 595 -> 1110 -> 1685)
    -   `_get_tasks` (lines 646 -> 1161 -> 1736)
    -   `_optimize_task` (lines 705 -> 1220 -> 1795)
    -   `adjust_memory_usage` (lines 723 -> 1238 -> 1813)
    -   `get_log_path` (lines 764 -> 1339 -> 1914)
    -   `clean_temp_files` (lines 776 -> 1351 -> 1926)
    -   `_cleanup_tasks` (lines 924 -> 1499)
    -   `cleanup` (lines 942 -> 1517)
    -   `_clear_system_cache` (lines 1318 -> 1893)

## Priority: Medium ⚠️ (Potential Bugs / Code Cleanup)

-   [ ] **Unused Variables:** Remove or utilize unused local variables (`F841`) identified in:
    -   `src/core/performance_optimizer.py:741:13` (system_memory)
    -   `src/core/performance_optimizer.py:744:13` (memory_config)
    -   `src/gui/theme.py:32:5` (COLOR_TEXT_SECONDARY)
    -   `tests/test_integration.py:20:9` (test_config)
-   [ ] **Unused Imports:** Remove unused imports (`F401`) to clean up namespaces:
    -   `src/main.py:7:1` ('sys')
    -   `src/main.py:10:1` ('tkinter as tk')
    -   `tests/test_gui_components.py:2:1` ('unittest.mock.MagicMock')
    -   `tests/test_performance_optimizer.py:4:1` ('psutil')
    -   `tests/test_performance_optimizer.py:5:1` ('os')

## Priority: Low 🧹 (Style / Readability Improvements)

-   [ ] **Line Length:** Address numerous `E501 line too long` errors across most project files. Consider reformatting code, breaking down long lines, or configuring flake8 to allow slightly longer lines if appropriate for the project standard (though PEP 8 standard is 79 characters). (See `run_tasks.log` for full list).
    -   *Files affected include:* `accessibility_manager.py`, `base_manager.py`, `config_manager.py`, `data_analyzer.py`, `environment_manager.py`, `feature_flags.py`, `i18n_manager.py`, `logging_manager.py`, `monitoring_manager.py`, `performance_optimizer.py`, `sentinel_core.py`, `sentinel_pc.py`, `service_layer.py`, `exceptions.py`, `gui_worker.py`, `pc_optimizer_gui.py`, `scrollable_frame.py`, `theme.py`, `main.py`, `test_cli_components.py`, `test_performance_optimizer.py`.
-   [ ] **Trailing Whitespace:** Remove trailing whitespace (`W291`) in `src/core/data_analyzer.py` (lines 124, 129, 134, 139).
-   [ ] **Blank Line Whitespace:** Remove whitespace from blank lines (`W293`) in `src/core/performance_optimizer.py` (lines 751, 755, 933, 953, 957, 1508, 1528, 1532).
-   [ ] **Whitespace Before Operator:** Fix `E203 whitespace before ':'` in `src/gui/pc_optimizer_gui.py` at line `149`.
