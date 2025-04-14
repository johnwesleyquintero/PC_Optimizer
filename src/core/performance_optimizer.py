# c:\Users\johnw\OneDrive\Desktop\SentinelPC\src\core\performance_optimizer.py
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
import concurrent.futures
import multiprocessing
import psutil
import platform
import os
import shutil
import datetime
import time

import configparser

# Assuming winreg is available on Windows for theme/startup management
try:
    import winreg

    _HAS_WINREG = True
except ImportError:
    _HAS_WINREG = False

from .base_manager import BasePerformanceOptimizer
from .config_manager import (
    ConfigManager,
)  # Using ConfigManager for consistency with SentinelCore
from .logging_manager import LoggingManager


# --- Custom Exceptions ---


class OptimizationError(Exception):
    """Base exception for optimization-related errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.details = details or {}
        super().__init__(f"{message} Details: {self.details}")


class ConfigurationError(OptimizationError):
    """Exception raised for configuration-related issues."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"Configuration Error: {message}", details)


class TaskExecutionError(OptimizationError):
    """Exception raised when a specific optimization task fails."""

    def __init__(
        self, task_name: str, reason: str, details: Optional[Dict[str, Any]] = None
    ):
        self.task_name = task_name
        self.reason = reason
        message = f"Task '{task_name}' failed: {reason}"
        super().__init__(message, details)


class MemoryOptimizationError(OptimizationError):
    """Exception raised when memory optimization fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"Memory Optimization Error: {message}", details)


class FileCleanupError(OptimizationError):
    """Exception raised when temporary file cleanup fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"File Cleanup Error: {message}", details)


class DiskOperationError(OptimizationError):
    """Exception raised for disk-related operation failures."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"Disk Operation Error: {message}", details)


class StartupManagementError(OptimizationError):
    """Exception raised for startup program management failures."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"Startup Management Error: {message}", details)


# --- Performance Optimizer Class ---


class PerformanceOptimizer(BasePerformanceOptimizer):
    """
    Manages system performance optimization tasks with enhanced robustness and configurability.

    Provides methods to initialize, cleanup, execute optimization tasks based on profiles,
    manage startup programs, get disk usage, and report status.
    """

    # Define default task configurations here or load from a separate default config file
    DEFAULT_TASKS_CONFIG = {
        "memory_optimization": {
            "function": "adjust_memory_usage",
            "priority": 1,
            "critical": True,
            "timeout": 300,
            "enabled": True,
        },
        "temp_cleanup": {
            "function": "clean_temp_files",
            "priority": 2,
            "critical": False,
            "timeout": 600,
            "enabled": True,
        },
        "disk_defrag": {  # Example: Added disk defrag task (Windows only)
            "function": "defragment_disk",
            "priority": 3,
            "critical": False,
            "timeout": 3600,
            "enabled": True,
            "os": "Windows",
        },
        "windows_theme_perf": {  # Example: Windows theme adjustment task
            "function": "adjust_windows_theme_performance",
            "priority": 4,
            "critical": False,
            "timeout": 60,
            "enabled": True,
            "os": "Windows",
            "params": {"optimize_for_performance": True},
        },
    }

    # Define default memory optimization settings
    DEFAULT_MEMORY_CONFIG = {
        "critical_threshold_gb": 2,
        "warning_threshold_gb": 4,
        "critical_max_threads": 2,
        "warning_max_threads": 4,
        "normal_max_threads": 8,  # Default if above warning
        "critical_priority": "high",  # Maps to psutil constants
        "warning_priority": "above_normal",
        "normal_priority": "normal",
        "clear_cache_critical": True,
        "clear_cache_warning": True,
        "clear_cache_normal": False,
    }

    # Define default temp file cleanup settings
    DEFAULT_CLEANUP_CONFIG = {
        "critical_disk_usage_percent": 90,
        "high_disk_usage_percent": 75,
        "critical_age_threshold_days": 1,
        "high_age_threshold_days": 7,
        "normal_age_threshold_days": 30,
        "patterns": {
            "temp_files": ["*.tmp", "*.temp", "~*", "*.bak", "*.old"],
            "log_files": ["*.log", "*.log.*", "*.dmp"],
            "cache_files": ["*.cache", "*.chk", "*.nch"],
            "download_artifacts": ["*.crdownload", "*.part", "*.download"],
        },
        "skip_prefixes": ["sys", "config", "important"],  # Example prefixes to skip
    }

    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initializes the PerformanceOptimizer.

        Args:
            config_manager: An instance of ConfigManager. If None, a new one is created.
        """
        self.logger = LoggingManager().get_logger(__name__)
        self.config_manager = config_manager or ConfigManager()
        self.config = self.config_manager.config  # Direct access to configparser object
        self._status = "idle"
        self._last_run_result: Optional[Dict[str, Any]] = None
        self._current_task: Optional[str] = None
        self._theme_settings: Dict[str, Any] = {}
        self._executor: Optional[ThreadPoolExecutor] = None
        self._tasks: Dict[str, Callable] = self._map_task_functions()

    def _map_task_functions(self) -> Dict[str, Callable]:
        """Maps task function names (str) to actual methods."""
        return {
            "adjust_memory_usage": self.adjust_memory_usage,
            "clean_temp_files": self.clean_temp_files,
            "defragment_disk": self.defragment_disk,
            "adjust_windows_theme_performance": self.adjust_windows_theme_performance,
            # Add other task functions here
        }

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Initialize the performance optimizer.

        Args:
            config: Optional dictionary to update the configuration.
                    (Note: ConfigManager handles loading, this is for potential overrides)

        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        try:
            self.logger.info("Initializing performance optimizer")
            # ConfigManager should be initialized before this point.
            # If specific overrides are passed, handle them (though update_config is preferred)
            if config:
                self.logger.warning(
                    "Initializing with direct config dict - prefer using ConfigManager update methods."
                )
                # This part needs careful implementation based on how ConfigManager handles updates
                # For now, we assume ConfigManager is already loaded correctly.

            # Initialize Windows theme performance settings if applicable
            if platform.system() == "Windows" and _HAS_WINREG:
                self._init_windows_theme_performance()

            self._status = "idle"
            self.logger.info("Performance optimizer initialized successfully.")
            return True
        except Exception as e:
            self.logger.error(
                f"Failed to initialize performance optimizer: {e}", exc_info=True
            )
            self._status = "error"
            return False

    def _init_windows_theme_performance(self) -> None:
        """Initialize and store Windows theme-related performance settings."""
        if not _HAS_WINREG:
            self.logger.warning(
                "Winreg module not found, cannot initialize Windows theme settings."
            )
            return
        try:
            theme_keys = {
                "SystemUsesLightTheme": (
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
                ),
                "AppsUseLightTheme": (
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
                ),
                "EnableTransparency": (
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
                ),
                # Add other relevant keys like visual effects if needed
                "VisualFXSetting": (
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects",
                ),
            }

            self._theme_settings = {}
            for setting, (hkey, path) in theme_keys.items():
                try:
                    with winreg.OpenKey(hkey, path, 0, winreg.KEY_READ) as key:
                        value, reg_type = winreg.QueryValueEx(key, setting)
                        self._theme_settings[setting] = value
                        self.logger.debug(f"Read theme setting '{setting}': {value}")
                except FileNotFoundError:
                    self.logger.debug(
                        f"Registry key or value not found for {setting} at {path}. Skipping."
                    )
                except OSError as e:
                    self.logger.warning(
                        f"Could not read {setting} from registry path {path}: {e}"
                    )

            self.logger.info("Windows theme performance settings initialized.")
        except Exception as e:
            self.logger.error(
                f"Failed to initialize Windows theme performance settings: {e}",
                exc_info=True,
            )
            # Don't raise here, initialization should still succeed if possible

    def adjust_windows_theme_performance(
        self, optimize_for_performance: bool = True
    ) -> Dict[str, Any]:
        """
        Adjust Windows theme settings for performance or restore originals.

        Args:
            optimize_for_performance: If True, optimize for performance; otherwise, restore originals.

        Returns:
            Dict[str, Any]: Result dictionary with success status and details.
        """
        result = {"success": False, "details": "", "changes": {}}
        if platform.system() != "Windows":
            result["details"] = "Windows theme optimization only available on Windows."
            self.logger.info(result["details"])
            return result
        if not _HAS_WINREG:
            result["details"] = (
                "Winreg module not found, cannot adjust Windows theme settings."
            )
            self.logger.warning(result["details"])
            return result

        try:
            target_settings = {}
            if optimize_for_performance:
                self.logger.info("Optimizing Windows theme for performance.")
                # Define performance settings (example)
                target_settings = {
                    "SystemUsesLightTheme": 1,  # Light theme often uses fewer resources
                    "AppsUseLightTheme": 1,
                    "EnableTransparency": 0,  # Disable transparency
                    "VisualFXSetting": 2,  # Adjust for best performance (value might vary)
                }
                result["details"] = "Optimized theme for performance."
            else:
                self.logger.info("Restoring original Windows theme settings.")
                if not self._theme_settings:
                    result["details"] = "No original theme settings found to restore."
                    self.logger.warning(result["details"])
                    return result  # Cannot restore if originals weren't read
                target_settings = self._theme_settings
                result["details"] = "Restored original theme settings."

            theme_key_path = (
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            )
            visual_fx_key_path = (
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects"
            )

            for setting, value in target_settings.items():
                key_path = (
                    theme_key_path
                    if setting != "VisualFXSetting"
                    else visual_fx_key_path
                )
                try:
                    # Ensure key exists before writing
                    with winreg.CreateKeyEx(
                        winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE
                    ) as key:
                        # Determine registry type (assuming DWORD for these examples)
                        reg_type = winreg.REG_DWORD
                        winreg.SetValueEx(key, setting, 0, reg_type, value)
                        result["changes"][setting] = value
                        self.logger.debug(f"Set theme setting '{setting}' to {value}")
                except OSError as e:
                    error_msg = f"Failed to update registry setting '{setting}': {e}"
                    self.logger.error(error_msg)
                    result["details"] = error_msg
                    result["success"] = (
                        False  # Mark as failed but continue trying others
                    )
                    # Consider if a single failure should abort the whole operation

            # If at least some changes were attempted, mark overall success based on errors
            result["success"] = not any(
                err in result["details"] for err in ["Failed", "not found"]
            )

            # TODO: Notify the system about the changes (e.g., broadcast WM_SETTINGCHANGE)
            # This often requires external libraries like ctypes or pywin32

            return result
        except Exception as e:
            error_msg = f"Failed to adjust Windows theme performance: {e}"
            self.logger.error(error_msg, exc_info=True)
            result["details"] = error_msg
            result["success"] = False
            return result

    def optimize_system(self, profile: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute system optimization tasks based on a profile using parallel processing.

        Args:
            profile: Optional optimization profile name (defined in config). Uses default if None.

        Returns:
            Dict containing overall success, tasks completed/failed, details, and timestamp.

        Raises:
            ConfigurationError: If configuration is invalid or profile not found.
            TaskExecutionError: If critical tasks fail during execution.
            OptimizationError: For other general optimization failures.
        """
        if self._status == "running":
            raise OptimizationError("Optimization is already running.")

        self._status = "running"
        self._current_task = "initializing"
        start_time = time.monotonic()

        try:
            self.logger.info(
                f"Starting system optimization with profile: {profile or 'default'}"
            )
            self._validate_optimization_ready()
            tasks_config = self._get_tasks_for_profile(profile)

            if not tasks_config:
                self.logger.warning(
                    "No optimization tasks found or enabled for this profile."
                )
                self._status = "completed"
                return {
                    "success": True,
                    "message": "No tasks to execute for the selected profile.",
                    "tasks_completed": 0,
                    "tasks_failed": 0,
                    "failed_tasks_details": [],
                    "warnings": [],
                    "duration_seconds": time.monotonic() - start_time,
                    "timestamp": datetime.datetime.now().isoformat(),
                }

            max_workers = self._get_thread_count()
            self.logger.info(f"Using {max_workers} worker threads for optimization.")
            with ThreadPoolExecutor(max_workers=max_workers) as self._executor:
                results = self._execute_tasks(self._executor, tasks_config)

            self._executor = None  # Clear executor reference after use
            report = self._generate_optimization_report(results)
            report["duration_seconds"] = round(time.monotonic() - start_time, 2)
            self._last_run_result = report
            self._status = "completed" if report["success"] else "failed"
            self.logger.info(
                f"Optimization finished. Success: {report['success']}. Duration: {report['duration_seconds']}s"
            )
            return report

        except (ConfigurationError, TaskExecutionError, OptimizationError) as opt_err:
            self.logger.error(f"Optimization failed: {opt_err}", exc_info=True)
            self._status = "failed"
            self._last_run_result = {
                "success": False,
                "error": str(opt_err),
                "details": opt_err.details,
            }
            raise  # Re-raise the specific optimization error
        except Exception as error:
            error_msg = f"Unexpected error during optimization: {error}"
            self.logger.error(error_msg, exc_info=True)
            self._status = "failed"
            self._last_run_result = {"success": False, "error": error_msg}
            raise OptimizationError(error_msg, {"error_type": "unexpected"}) from error
        finally:
            self._current_task = None  # Reset current task when done or failed

    def _validate_optimization_ready(self) -> None:
        """Verify system meets basic requirements before starting optimization."""
        self.logger.debug("Validating optimization readiness.")
        # Basic check: Ensure config is loaded (ConfigManager handles actual loading errors)
        if not self.config or not isinstance(self.config, configparser.ConfigParser):
            raise ConfigurationError("Configuration is not loaded or invalid.")

        # Check system resources (optional, can be made configurable)
        try:
            if not self._check_system_resources():
                self.logger.warning(
                    "System resources are currently high, optimization might be less effective."
                )
                # Decide whether to raise an error or just warn based on config/policy
                # raise OptimizationError("Insufficient system resources for optimization")
        except Exception as e:
            self.logger.warning(
                f"Failed to check system resources: {e}. Proceeding with optimization."
            )

        self.logger.debug("Optimization readiness validation passed.")

    def _check_system_resources(self) -> bool:
        """Check if system has sufficient resources (example thresholds)."""
        try:
            cpu_threshold = float(
                self.config.get("Performance", "readiness_cpu_threshold", fallback=95.0)
            )
            mem_threshold = float(
                self.config.get("Performance", "readiness_mem_threshold", fallback=98.0)
            )
            min_mem_mb = int(
                self.config.get("Performance", "readiness_min_mem_mb", fallback=256)
            )

            cpu_percent = psutil.cpu_percent(
                interval=0.5
            )  # Shorter interval for readiness check
            memory = psutil.virtual_memory()

            sufficient = (
                cpu_percent < cpu_threshold
                and memory.percent < mem_threshold
                and memory.available >= min_mem_mb * 1024 * 1024
            )
            if not sufficient:
                self.logger.warning(
                    f"Resource check: CPU={cpu_percent:.1f}% (Threshold={cpu_threshold}%), "
                    f"Mem={memory.percent:.1f}% (Threshold={mem_threshold}%), "
                    f"AvailMem={memory.available / (1024*1024):.0f}MB (Min={min_mem_mb}MB)"
                )
            return sufficient
        except Exception as e:
            self.logger.warning(
                f"Failed to check system resources during readiness check: {e}"
            )
            return True  # Assume resources are sufficient if check fails to avoid blocking optimization

    def _get_thread_count(self) -> int:
        """Determine optimal thread count based on config and system resources."""
        try:
            cpu_count = multiprocessing.cpu_count()
            # Get max_threads from config, default to cpu_count - 1 (or 1 if single core)
            config_max_threads = self.config.getint(
                "Performance", "max_threads", fallback=max(1, cpu_count - 1)
            )

            # Simple logic: use the configured value, capped by CPU count.
            # More complex logic could consider memory as well.
            thread_count = max(1, min(config_max_threads, cpu_count))
            self.logger.debug(
                f"Determined thread count: {thread_count} (ConfigMax: {config_max_threads}, CPUCores: {cpu_count})"
            )
            return thread_count
        except Exception as e:
            self.logger.error(
                f"Failed to determine thread count: {e}. Defaulting to 1.",
                exc_info=True,
            )
            return 1

    def _get_tasks_for_profile(
        self, profile: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get list of optimization task configurations for a given profile.

        Loads tasks from the configuration file based on the profile.
        Falls back to default tasks if profile is not found or invalid.

        Args:
            profile: The name of the optimization profile.

        Returns:
            List[Dict[str, Any]]: A list of task configuration dictionaries.

        Raises:
            ConfigurationError: If the profile definition is fundamentally broken.
        """
        profile_name = profile or self.config.get(
            "Profiles", "default", fallback="default"
        )
        self.logger.info(f"Loading tasks for profile: '{profile_name}'")
        profile_section = f"OptimizationProfile:{profile_name}"

        tasks_to_run = []

        if self.config.has_section(profile_section):
            self.logger.debug(f"Found profile section: {profile_section}")
            profile_tasks = self.config.items(profile_section)
            defined_tasks = dict(profile_tasks)

            # Iterate through default tasks to maintain structure and defaults
            for task_name, default_config in self.DEFAULT_TASKS_CONFIG.items():
                task_config = default_config.copy()  # Start with default

                # Check if task is defined and enabled in the profile
                profile_setting = defined_tasks.get(
                    task_name.lower()
                )  # Config keys are lowercased
                if profile_setting is not None:
                    try:
                        # Profile can override 'enabled', 'priority', 'timeout', 'params'
                        parts = [p.strip() for p in profile_setting.split(";")]
                        task_config["enabled"] = parts[0].lower() == "true"
                        if len(parts) > 1:
                            task_config["priority"] = int(parts[1])
                        if len(parts) > 2:
                            task_config["timeout"] = int(parts[2])
                        if len(parts) > 3:  # Parse simple key=value params
                            params = {}
                            for kv in parts[3:]:
                                if "=" in kv:
                                    k, v = kv.split("=", 1)
                                    # Attempt basic type conversion
                                    if v.lower() == "true":
                                        params[k.strip()] = True
                                    elif v.lower() == "false":
                                        params[k.strip()] = False
                                    elif v.isdigit():
                                        params[k.strip()] = int(v)
                                    elif v.replace(".", "", 1).isdigit():
                                        params[k.strip()] = float(v)
                                    else:
                                        params[k.strip()] = v
                            task_config["params"] = params

                    except (ValueError, IndexError) as e:
                        self.logger.warning(
                            f"Invalid format for task '{task_name}' in profile '{profile_name}': '{profile_setting}'. Using defaults. Error: {e}"
                        )
                        # Keep default enabled/priority/timeout if parsing fails
                        task_config["enabled"] = default_config.get(
                            "enabled", False
                        )  # Revert to default enabled state
                else:
                    # Task not mentioned in profile, use default enabled state
                    task_config["enabled"] = default_config.get("enabled", False)

                # Add task if enabled and meets OS requirement
                os_match = (
                    "os" not in task_config or task_config["os"] == platform.system()
                )
                if task_config.get("enabled", False) and os_match:
                    task_config["name"] = task_name
                    if task_config["function"] not in self._tasks:
                        self.logger.error(
                            f"Task function '{task_config['function']}' for task '{task_name}' is not implemented."
                        )
                        continue  # Skip unimplemented tasks
                    tasks_to_run.append(task_config)
                    self.logger.debug(
                        f"Added task '{task_name}' from profile '{profile_name}' with config: {task_config}"
                    )

        else:
            self.logger.warning(
                f"Profile section '{profile_section}' not found. Using default tasks."
            )
            # Fallback to default tasks if profile section doesn't exist
            for task_name, default_config in self.DEFAULT_TASKS_CONFIG.items():
                task_config = default_config.copy()
                os_match = (
                    "os" not in task_config or task_config["os"] == platform.system()
                )
                if task_config.get("enabled", False) and os_match:
                    task_config["name"] = task_name
                    if task_config["function"] not in self._tasks:
                        self.logger.error(
                            f"Task function '{task_config['function']}' for task '{task_name}' is not implemented."
                        )
                        continue
                    tasks_to_run.append(task_config)
                    self.logger.debug(
                        f"Added default task '{task_name}' with config: {task_config}"
                    )

        # Validate and sort tasks
        valid_tasks = []
        for task in tasks_to_run:
            if not all(k in task for k in ("name", "function", "priority")):
                self.logger.error(
                    f"Invalid task configuration structure for {task.get('name', 'unknown')}: Missing required keys. Skipping."
                )
                continue
            valid_tasks.append(task)

        return sorted(valid_tasks, key=lambda x: x["priority"])

    def _execute_tasks(
        self, executor: ThreadPoolExecutor, tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Execute optimization tasks in parallel using the provided executor.

        Args:
            executor: ThreadPoolExecutor instance.
            tasks: List of task configurations to execute.

        Returns:
            List[Dict[str, Any]]: Results of task execution, including success, details, and errors.
        """
        futures: Dict[concurrent.futures.Future, Dict[str, Any]] = {}
        results = []

        self.logger.info(f"Executing {len(tasks)} optimization tasks...")

        for task_config in tasks:
            task_name = task_config["name"]
            task_func = self._tasks[task_config["function"]]
            task_params = task_config.get("params", {})
            task_timeout = task_config.get("timeout", 300)  # Default 5 min timeout

            self.logger.debug(
                f"Submitting task: {task_name} with params: {task_params}, timeout: {task_timeout}s"
            )
            future = executor.submit(
                self._optimize_task_wrapper, task_name, task_func, task_params
            )
            futures[future] = task_config  # Store full config for context

        for future in concurrent.futures.as_completed(futures.keys()):
            task_config = futures[future]
            task_name = task_config["name"]
            task_timeout = task_config.get("timeout", 300)

            try:
                # Use the task-specific timeout if available
                result = future.result(timeout=task_timeout)
                results.append(result)
                self.logger.info(
                    f"Task '{task_name}' completed. Success: {result.get('success')}"
                )
            except FuturesTimeoutError:
                error_msg = (
                    f"Task '{task_name}' timed out after {task_timeout} seconds."
                )
                self.logger.error(error_msg)
                results.append(
                    {
                        "name": task_name,
                        "success": False,
                        "error": "timeout",
                        "details": error_msg,
                        "critical": task_config.get("critical", False),
                    }
                )
                # Optionally attempt to cancel the future if needed, though result() already waited
                # future.cancel()
            except Exception as e:
                error_msg = f"Task '{task_name}' failed with an unexpected error: {e}"
                self.logger.error(error_msg, exc_info=True)
                results.append(
                    {
                        "name": task_name,
                        "success": False,
                        "error": str(e),
                        "details": error_msg,
                        "critical": task_config.get("critical", False),
                    }
                )

        return results

    def _optimize_task_wrapper(
        self, task_name: str, task_func: Callable, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Wrapper to execute a single task, handle its state, and capture results/errors.

        Args:
            task_name: Name of the task.
            task_func: The actual task function to call.
            params: Dictionary of parameters to pass to the task function.

        Returns:
            Dict[str, Any]: Result dictionary including name, success, details, error.
        """
        self._current_task = task_name
        self.logger.info(f"Starting task: {task_name}")
        start_time = time.monotonic()
        try:
            # Execute the task function with its parameters
            task_result = task_func(**params)

            # Standardize result format
            if isinstance(task_result, dict) and "success" in task_result:
                result_dict = task_result
            elif isinstance(task_result, bool):  # Handle simple boolean returns
                result_dict = {
                    "success": task_result,
                    "details": "Task returned boolean.",
                }
            else:  # Handle unexpected return types
                self.logger.warning(
                    f"Task '{task_name}' returned unexpected type: {type(task_result)}. Assuming success=True."
                )
                result_dict = {
                    "success": True,
                    "details": f"Task returned non-standard type: {type(task_result)}",
                }

            result_dict["name"] = task_name
            result_dict["duration_seconds"] = round(time.monotonic() - start_time, 2)
            self.logger.info(
                f"Finished task: {task_name} in {result_dict['duration_seconds']:.2f}s. Success: {result_dict['success']}"
            )
            return result_dict

        except (
            OptimizationError,
            ConfigurationError,
            TaskExecutionError,
            MemoryOptimizationError,
            FileCleanupError,
            DiskOperationError,
            StartupManagementError,
        ) as opt_err:
            # Catch specific optimization errors raised by tasks
            duration = round(time.monotonic() - start_time, 2)
            error_msg = f"Task '{task_name}' failed after {duration:.2f}s: {opt_err}"
            self.logger.error(error_msg, exc_info=True)
            return {
                "name": task_name,
                "success": False,
                "error": type(opt_err).__name__,
                "details": str(opt_err),
                "duration_seconds": duration,
            }
        except Exception as e:
            # Catch any other unexpected errors during task execution
            duration = round(time.monotonic() - start_time, 2)
            error_msg = f"Task '{task_name}' encountered an unexpected error after {duration:.2f}s: {e}"
            self.logger.error(error_msg, exc_info=True)
            return {
                "name": task_name,
                "success": False,
                "error": "unexpected",
                "details": error_msg,
                "duration_seconds": duration,
            }
        finally:
            self._current_task = None  # Clear current task after execution

    def _generate_optimization_report(
        self, results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate a summary report from the results of individual tasks.

        Args:
            results: List of task execution result dictionaries.

        Returns:
            Dict[str, Any]: Detailed optimization report.

        Raises:
            TaskExecutionError: If any critical tasks failed.
        """
        report = {
            "success": True,
            "message": "Optimization completed.",
            "tasks_completed": 0,
            "tasks_failed": 0,
            "failed_tasks_details": [],
            "warnings": [],
            "task_results": results,  # Include individual results
            "timestamp": datetime.datetime.now().isoformat(),
        }
        critical_failures = []

        for result in results:
            task_name = result.get("name", "unknown_task")
            if result.get("success", False):
                report["tasks_completed"] += 1
            else:
                report["success"] = False  # Overall success is false if any task fails
                report["tasks_failed"] += 1
                failure_detail = {
                    "name": task_name,
                    "error": result.get("error", "Unknown error"),
                    "details": result.get("details", ""),
                    "critical": result.get(
                        "critical", False
                    ),  # Check if the task was marked critical
                    "duration_seconds": result.get("duration_seconds"),
                }
                report["failed_tasks_details"].append(failure_detail)
                if failure_detail["critical"]:
                    critical_failures.append(task_name)

            if "warning" in result and result["warning"]:
                report["warnings"].append(f"Task '{task_name}': {result['warning']}")

        if not report["success"]:
            report["message"] = (
                f"Optimization completed with {report['tasks_failed']} failed task(s)."
            )

        # Raise an error if critical tasks failed
        if critical_failures:
            failure_names = ", ".join(critical_failures)
            error_msg = f"Critical tasks failed during optimization: {failure_names}"
            self.logger.error(error_msg)
            # Include failed task details in the exception
            raise TaskExecutionError(
                task_name=failure_names,
                reason="Critical optimization tasks failed",
                details={"critical_failures": report["failed_tasks_details"]},
            )

        return report

    def get_optimization_status(self) -> Dict[str, Any]:
        """
        Get the current status of the performance optimizer.

        Returns:
            Dict containing status, last run result (if any), and current task (if running).
        """
        return {
            "success": True,
            "status": self._status,
            "last_run_result": self._last_run_result,
            "current_task": self._current_task,
            "timestamp": datetime.datetime.now().isoformat(),
        }

    # --- Specific Optimization Task Implementations ---

    def adjust_memory_usage(self) -> Dict[str, Any]:
        """
        Adjust system memory usage based on available memory and configuration.

        Reads thresholds and actions from the configuration file.

        Returns:
            Dict[str, Any]: Result dictionary with success status and details.

        Raises:
            MemoryOptimizationError: If memory adjustment fails significantly.
            ConfigurationError: If memory configuration is missing or invalid.
        """
        self.logger.info("Adjusting memory usage based on configuration.")
        result = {
            "success": False,
            "details": "",
            "state": "unknown",
            "actions_taken": [],
        }
        try:
            system_memory = psutil.virtual_memory()
            available_gb = system_memory.available / (1024**3)
            usage_percent = system_memory.percent

            # Load memory config with defaults
            config_section = "MemoryOptimization"
            mem_cfg = self.DEFAULT_MEMORY_CONFIG.copy()  # Start with defaults
            if self.config.has_section(config_section):
                for key, default_val in self.DEFAULT_MEMORY_CONFIG.items():
                    if isinstance(default_val, bool):
                        mem_cfg[key] = self.config.getboolean(
                            config_section, key, fallback=default_val
                        )
                    elif isinstance(default_val, int):
                        mem_cfg[key] = self.config.getint(
                            config_section, key, fallback=default_val
                        )
                    elif isinstance(default_val, float):
                        mem_cfg[key] = self.config.getfloat(
                            config_section, key, fallback=default_val
                        )
                    else:  # String priorities
                        mem_cfg[key] = self.config.get(
                            config_section, key, fallback=default_val
                        )
            else:
                self.logger.warning(
                    f"Configuration section '[{config_section}]' not found. Using default memory settings."
                )

            # Determine current memory state based on AVAILABLE memory (more reliable than percentage)
            if available_gb < mem_cfg["critical_threshold_gb"]:
                current_state = "critical"
            elif available_gb < mem_cfg["warning_threshold_gb"]:
                current_state = "warning"
            else:
                current_state = "normal"
            result["state"] = current_state
            self.logger.info(
                f"Memory state: {current_state} (Available: {available_gb:.2f}GB, Usage: {usage_percent:.1f}%)"
            )

            # Apply optimizations based on state
            state_max_threads = mem_cfg[f"{current_state}_max_threads"]
            state_priority_str = mem_cfg[f"{current_state}_priority"]
            state_clear_cache = mem_cfg[f"{current_state}_clear_cache"]

            # 1. Update thread configuration (if different from current Performance setting)
            # Note: This modifies the main config, potentially affecting other operations.
            # Consider if this should be temporary or persistent.
            current_max_threads = self.config.getint(
                "Performance", "max_threads", fallback=multiprocessing.cpu_count()
            )
            if current_max_threads != state_max_threads:
                try:
                    self.config.set(
                        "Performance", "max_threads", str(state_max_threads)
                    )
                    # No need to call save_config here, let cleanup handle it or rely on ConfigManager's auto-save
                    self.logger.info(
                        f"Set max_threads to {state_max_threads} due to memory state '{current_state}'."
                    )
                    result["actions_taken"].append(
                        f"set_max_threads={state_max_threads}"
                    )
                except Exception as e:
                    self.logger.error(f"Failed to update max_threads in config: {e}")
                    # Non-critical error, continue

            # 2. Adjust process priority (Windows only)
            if platform.system() == "Windows":
                priority_map = {
                    "low": psutil.IDLE_PRIORITY_CLASS,
                    "below_normal": psutil.BELOW_NORMAL_PRIORITY_CLASS,
                    "normal": psutil.NORMAL_PRIORITY_CLASS,
                    "above_normal": psutil.ABOVE_NORMAL_PRIORITY_CLASS,
                    "high": psutil.HIGH_PRIORITY_CLASS,
                    "realtime": psutil.REALTIME_PRIORITY_CLASS,
                }
                target_priority = priority_map.get(
                    state_priority_str.lower(), psutil.NORMAL_PRIORITY_CLASS
                )
                try:
                    current_process = psutil.Process()
                    current_priority = current_process.nice()
                    if current_priority != target_priority:
                        current_process.nice(target_priority)
                        self.logger.info(
                            f"Set process priority to '{state_priority_str}' ({target_priority}) due to memory state '{current_state}'."
                        )
                        result["actions_taken"].append(
                            f"set_priority={state_priority_str}"
                        )
                except psutil.Error as e:
                    self.logger.warning(f"Failed to set process priority: {e}")
                    result["warning"] = f"Failed to set process priority: {e}"

            # 3. Clear system cache if needed
            if state_clear_cache:
                self.logger.info(
                    f"Triggering system cache clear due to memory state '{current_state}'."
                )
                cache_clear_result = self._clear_system_cache()
                result["actions_taken"].append(
                    f"clear_cache={cache_clear_result['success']}"
                )
                if not cache_clear_result["success"]:
                    result["warning"] = (
                        result.get("warning", "")
                        + f" Cache clearing failed: {cache_clear_result['details']}"
                    )

            result["success"] = True  # Mark success if actions were attempted
            result["details"] = (
                f"Memory adjustments applied for state '{current_state}'. Available: {available_gb:.2f}GB."
            )
            return result

        except configparser.Error as e:
            error_msg = f"Invalid memory configuration: {e}"
            self.logger.error(error_msg, exc_info=True)
            raise ConfigurationError(
                error_msg, {"section": "MemoryOptimization"}
            ) from e
        except Exception as e:
            error_msg = f"Failed to adjust memory usage: {e}"
            self.logger.error(error_msg, exc_info=True)
            # Raise a specific error if adjustment fails critically
            raise MemoryOptimizationError(
                error_msg,
                {"available_gb": available_gb, "usage_percent": usage_percent},
            ) from e

    def _clear_system_cache(self) -> Dict[str, Any]:
        """
        Attempt to clear system caches (OS-dependent).

        Returns:
            Dict[str, Any]: Result dictionary with success status and details.
        """
        result = {"success": False, "details": "Not implemented for this OS."}
        self.logger.info("Attempting to clear system cache...")
        try:
            if platform.system() == "Windows":
                # Attempt 1: Python garbage collection (minor effect)
                import gc

                gc.collect()
                self.logger.debug("Python garbage collection triggered.")

                # Attempt 2: Clear DNS Cache (requires admin usually)
                try:
                    # Use subprocess for better error handling than os.system
                    import subprocess

                    subprocess.run(
                        ["ipconfig", "/flushdns"],
                        check=True,
                        capture_output=True,
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW,
                    )
                    self.logger.info("DNS cache flushed successfully.")
                    result["details"] = "DNS cache flushed. "
                except (subprocess.CalledProcessError, FileNotFoundError) as dns_err:
                    self.logger.warning(
                        f"Failed to flush DNS cache (requires admin?): {dns_err}"
                    )
                    result["details"] = f"DNS cache flush failed ({dns_err}). "

                # Attempt 3: Clear Windows Update Cache (requires admin)
                # More complex: Stop service, delete folder contents, restart service
                # Example (simplified, needs error handling and admin rights):
                # os.system('net stop wuauserv')
                # shutil.rmtree(r'C:\Windows\SoftwareDistribution\Download', ignore_errors=True)
                # os.system('net start wuauserv')
                # self.logger.info("Attempted to clear Windows Update cache.")
                # result["details"] += "Attempted WU cache clear. "
                # For now, just log that it's complex
                self.logger.info(
                    "Windows Update cache clearing is complex and requires admin rights, skipping for now."
                )
                result["details"] += "WU cache clear skipped. "

                # Add other cache clearing methods if known (e.g., specific app caches)

                result["success"] = (
                    True  # Mark success if attempts were made, even if some failed
                )

            elif platform.system() == "Linux":
                # Attempt 1: Sync filesystem buffers
                os.system("sync")
                # Attempt 2: Drop caches (requires root)
                # Check if running as root before attempting
                if os.geteuid() == 0:
                    try:
                        with open("/proc/sys/vm/drop_caches", "w") as f:
                            f.write("3")  # Drop pagecache, dentries and inodes
                        self.logger.info(
                            "Linux caches dropped successfully (pagecache, dentries, inodes)."
                        )
                        result["details"] = "Linux caches dropped."
                        result["success"] = True
                    except IOError as e:
                        self.logger.warning(
                            f"Failed to drop Linux caches (permission error?): {e}"
                        )
                        result["details"] = f"Failed to drop Linux caches: {e}"
                else:
                    self.logger.warning(
                        "Cannot drop Linux caches: requires root privileges."
                    )
                    result["details"] = "Cannot drop Linux caches (requires root)."
                # Success is True if sync worked, even if drop_caches failed due to permissions

            elif platform.system() == "Darwin":  # macOS
                # Attempt 1: Purge inactive memory (requires sudo)
                try:
                    import subprocess

                    subprocess.run(
                        ["sudo", "purge"], check=True, capture_output=True, text=True
                    )
                    self.logger.info("macOS inactive memory purged successfully.")
                    result["details"] = "macOS inactive memory purged."
                    result["success"] = True
                except (subprocess.CalledProcessError, FileNotFoundError) as purge_err:
                    self.logger.warning(
                        f"Failed to purge macOS memory (requires sudo?): {purge_err}"
                    )
                    result["details"] = f"Failed to purge macOS memory: {purge_err}"

            else:
                self.logger.info(
                    f"Cache clearing not implemented for OS: {platform.system()}"
                )

        except Exception as e:
            error_msg = f"Unexpected error during cache clearing: {e}"
            self.logger.error(error_msg, exc_info=True)
            result["details"] = error_msg
            result["success"] = False

        return result

    def clean_temp_files(self) -> Dict[str, Any]:
        """
        Clean temporary files based on age, patterns, and disk usage thresholds from config.

        Returns:
            Dict[str, Any]: Cleanup operation results including success status,
                          files removed count, space freed (approx), and any errors.

        Raises:
            FileCleanupError: If cleanup process encounters critical errors.
            ConfigurationError: If cleanup configuration is invalid.
        """
        self.logger.info("Starting temporary file cleanup.")
        result = {
            "success": False,
            "files_removed": 0,
            "dirs_removed": 0,
            "space_freed_bytes": 0,
            "files_preserved": 0,
            "errors": [],
            "details": "",
        }
        temp_dirs_to_clean = []
        total_space_before = 0
        config_section = "TempFileCleanup"

        try:
            # Load cleanup config with defaults
            cleanup_cfg = self.DEFAULT_CLEANUP_CONFIG.copy()
            if self.config.has_section(config_section):
                cleanup_cfg["critical_disk_usage_percent"] = self.config.getfloat(
                    config_section,
                    "critical_disk_usage_percent",
                    fallback=cleanup_cfg["critical_disk_usage_percent"],
                )
                cleanup_cfg["high_disk_usage_percent"] = self.config.getfloat(
                    config_section,
                    "high_disk_usage_percent",
                    fallback=cleanup_cfg["high_disk_usage_percent"],
                )
                cleanup_cfg["critical_age_threshold_days"] = self.config.getint(
                    config_section,
                    "critical_age_threshold_days",
                    fallback=cleanup_cfg["critical_age_threshold_days"],
                )
                cleanup_cfg["high_age_threshold_days"] = self.config.getint(
                    config_section,
                    "high_age_threshold_days",
                    fallback=cleanup_cfg["high_age_threshold_days"],
                )
                cleanup_cfg["normal_age_threshold_days"] = self.config.getint(
                    config_section,
                    "normal_age_threshold_days",
                    fallback=cleanup_cfg["normal_age_threshold_days"],
                )
                # Load patterns (assuming JSON or comma-separated in config)
                try:
                    patterns_str = self.config.get(
                        config_section,
                        "patterns",
                        fallback=str(cleanup_cfg["patterns"]),
                    )
                    # Basic parsing assuming dict-like string or JSON string
                    import json

                    try:
                        cleanup_cfg["patterns"] = json.loads(
                            patterns_str.replace("'", '"')
                        )
                    except json.JSONDecodeError:
                        self.logger.warning(
                            f"Could not parse patterns from config string: {patterns_str}. Using defaults."
                        )
                        cleanup_cfg["patterns"] = self.DEFAULT_CLEANUP_CONFIG[
                            "patterns"
                        ]
                except Exception as pattern_err:
                    self.logger.warning(
                        f"Error loading patterns from config: {pattern_err}. Using defaults."
                    )
                    cleanup_cfg["patterns"] = self.DEFAULT_CLEANUP_CONFIG["patterns"]

                # Load skip prefixes
                skip_prefixes_str = self.config.get(
                    config_section,
                    "skip_prefixes",
                    fallback=",".join(cleanup_cfg["skip_prefixes"]),
                )
                cleanup_cfg["skip_prefixes"] = [
                    p.strip() for p in skip_prefixes_str.split(",") if p.strip()
                ]
            else:
                self.logger.warning(
                    f"Configuration section '[{config_section}]' not found. Using default cleanup settings."
                )

            # Identify temporary directories
            env_vars = ["TEMP", "TMP"]
            if platform.system() == "Windows":
                env_vars.extend(
                    ["LOCALAPPDATA", "USERPROFILE"]
                )  # Look in AppData\Local\Temp too
            elif platform.system() == "Linux":
                temp_dirs_to_clean.append(Path("/tmp"))
                temp_dirs_to_clean.append(Path("/var/tmp"))
            elif platform.system() == "Darwin":
                temp_dirs_to_clean.append(Path("/private/var/tmp"))
                # Add user cache dir? Path.home() / "Library/Caches" - BE CAREFUL HERE

            for var in env_vars:
                if path_str := os.environ.get(var):
                    path = Path(path_str)
                    if (
                        var in ["LOCALAPPDATA", "USERPROFILE"]
                        and platform.system() == "Windows"
                    ):
                        path = path / "AppData" / "Local" / "Temp"  # Common location
                    if path.is_dir() and path not in temp_dirs_to_clean:
                        temp_dirs_to_clean.append(path)

            if not temp_dirs_to_clean:
                result["details"] = "No standard temporary directories found to clean."
                result["success"] = True
                self.logger.warning(result["details"])
                return result

            self.logger.info(
                f"Identified temp directories to scan: {[str(d) for d in temp_dirs_to_clean]}"
            )

            # Determine age threshold based on disk usage of the *first* temp dir found
            # A more robust approach might check usage for each mount point involved.
            try:
                usage = psutil.disk_usage(str(temp_dirs_to_clean[0]))
                used_percent = usage.percent
                total_space_before = usage.used  # Rough estimate
            except (FileNotFoundError, psutil.Error) as e:
                self.logger.warning(
                    f"Could not get disk usage for {temp_dirs_to_clean[0]}: {e}. Using normal age threshold."
                )
                used_percent = 0  # Assume normal usage

            if used_percent > cleanup_cfg["critical_disk_usage_percent"]:
                age_threshold_days = cleanup_cfg["critical_age_threshold_days"]
                cleanup_level = "aggressive"
            elif used_percent > cleanup_cfg["high_disk_usage_percent"]:
                age_threshold_days = cleanup_cfg["high_age_threshold_days"]
                cleanup_level = "standard"
            else:
                age_threshold_days = cleanup_cfg["normal_age_threshold_days"]
                cleanup_level = "conservative"

            self.logger.info(
                f"Disk usage at {used_percent:.1f}%. Applying '{cleanup_level}' cleanup (Age > {age_threshold_days} days)."
            )
            result["details"] = (
                f"Cleanup level: {cleanup_level} (Age > {age_threshold_days} days)."
            )

            current_time = time.time()
            age_threshold_secs = age_threshold_days * 24 * 3600

            # Iterate and clean
            for temp_dir in temp_dirs_to_clean:
                if not temp_dir.is_dir():
                    self.logger.debug(f"Skipping non-existent directory: {temp_dir}")
                    continue

                self.logger.info(f"Cleaning directory: {temp_dir}")
                # Use scandir for potentially better performance
                try:
                    for item in os.scandir(temp_dir):
                        try:
                            item_path = Path(item.path)
                            # Check skip prefixes
                            if any(
                                item.name.lower().startswith(p)
                                for p in cleanup_cfg["skip_prefixes"]
                            ):
                                self.logger.debug(
                                    f"Skipping '{item.name}' due to skip prefix."
                                )
                                result["files_preserved"] += 1
                                continue

                            # Check age
                            item_mtime = item.stat().st_mtime
                            item_age_secs = current_time - item_mtime
                            if item_age_secs < age_threshold_secs:
                                result["files_preserved"] += 1
                                continue  # Skip recent items

                            # Check patterns (apply only if configured, otherwise delete old items)
                            matches_pattern = False
                            if cleanup_cfg.get("patterns"):
                                for patterns in cleanup_cfg["patterns"].values():
                                    if any(item_path.match(p) for p in patterns):
                                        matches_pattern = True
                                        break
                            else:
                                matches_pattern = True  # Delete if no patterns specified and old enough

                            if not matches_pattern:
                                result["files_preserved"] += 1
                                continue  # Skip if patterns defined but item doesn't match

                            # Delete item
                            item_size = item.stat().st_size
                            if item.is_file() or item.is_symlink():
                                item_path.unlink(missing_ok=True)
                                result["files_removed"] += 1
                                result["space_freed_bytes"] += item_size
                                self.logger.debug(f"Removed file: {item_path}")
                            elif item.is_dir():
                                dir_size = sum(
                                    f.stat().st_size
                                    for f in item_path.glob("**/*")
                                    if f.is_file()
                                )  # Approx size
                                shutil.rmtree(item_path, ignore_errors=True)
                                result["dirs_removed"] += 1
                                result[
                                    "space_freed_bytes"
                                ] += dir_size  # Add estimated dir size
                                self.logger.debug(f"Removed directory: {item_path}")

                        except PermissionError as pe:
                            result["errors"].append(
                                {"path": item.path, "error": f"Permission denied: {pe}"}
                            )
                            self.logger.debug(
                                f"Permission denied for {item.path}: {pe}"
                            )
                        except OSError as oe:
                            result["errors"].append(
                                {"path": item.path, "error": f"OS error: {oe}"}
                            )
                            self.logger.warning(f"Failed to process {item.path}: {oe}")
                        except Exception as item_err:
                            result["errors"].append(
                                {
                                    "path": item.path,
                                    "error": f"Unexpected error: {item_err}",
                                }
                            )
                            self.logger.warning(
                                f"Unexpected error processing {item.path}: {item_err}",
                                exc_info=True,
                            )

                except PermissionError as dir_pe:
                    result["errors"].append(
                        {
                            "path": str(temp_dir),
                            "error": f"Permission denied accessing dir: {dir_pe}",
                        }
                    )
                    self.logger.warning(
                        f"Permission denied accessing directory {temp_dir}: {dir_pe}"
                    )
                except Exception as dir_err:
                    error_msg = f"Critical error while cleaning {temp_dir}: {dir_err}"
                    self.logger.error(error_msg, exc_info=True)
                    result["errors"].append({"path": str(temp_dir), "error": error_msg})
                    # Decide if this is critical enough to stop the whole task
                    # raise FileCleanupError(error_msg, {"directory": str(temp_dir)})

            result["success"] = not result["errors"]  # Success if no errors occurred
            space_freed_mb = result["space_freed_bytes"] / (1024 * 1024)
            result["details"] += (
                f" Removed {result['files_removed']} files, {result['dirs_removed']} dirs. "
                f"Freed approx {space_freed_mb:.2f} MB. "
                f"{result['files_preserved']} items preserved. {len(result['errors'])} errors."
            )
            self.logger.info(f"Temp file cleanup finished. {result['details']}")
            return result

        except configparser.Error as e:
            error_msg = f"Invalid cleanup configuration: {e}"
            self.logger.error(error_msg, exc_info=True)
            raise ConfigurationError(error_msg, {"section": config_section}) from e
        except Exception as e:
            error_msg = f"Failed to clean temporary files: {e}"
            self.logger.error(error_msg, exc_info=True)
            raise FileCleanupError(error_msg) from e

    def defragment_disk(self, drive_letter: Optional[str] = None) -> Dict[str, Any]:
        """
        Initiates disk defragmentation on Windows for a specific drive or the system drive.

        Args:
            drive_letter: The drive letter to defragment (e.g., "C"). If None, uses the system drive.

        Returns:
            Dict[str, Any]: Result dictionary with success status and details.

        Raises:
            DiskOperationError: If the operation fails or is not supported.
        """
        result = {"success": False, "details": "", "drive": ""}
        if platform.system() != "Windows":
            result["details"] = "Disk defragmentation is only supported on Windows."
            self.logger.warning(result["details"])
            return result

        try:
            target_drive = drive_letter
            if not target_drive:
                # Find system drive
                system_drive = os.getenv("SystemDrive", "C:")
                target_drive = system_drive.strip(":")
            result["drive"] = f"{target_drive}:"
            self.logger.info(
                f"Starting defragmentation analysis for drive {target_drive}:"
            )

            # Use Windows built-in defrag tool (defrag.exe)
            # Requires Administrator privileges
            import subprocess

            # Step 1: Analyze the drive
            analyze_cmd = ["defrag", f"{target_drive}:", "/A", "/U", "/V"]
            self.logger.debug(f"Running command: {' '.join(analyze_cmd)}")
            try:
                # Run with admin rights if possible, or inform user
                # Note: Running requires elevation which isn't directly handled here.
                # This will likely fail without admin rights.
                analysis_output = subprocess.run(
                    analyze_cmd,
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=300,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                self.logger.info(
                    f"Defrag analysis output for {target_drive}:\n{analysis_output.stdout}"
                )
                result["details"] = (
                    f"Analysis complete for {target_drive}:. Output logged."
                )
                # TODO: Parse analysis_output to determine if defrag is needed

                # Step 2: Optionally run defragmentation if needed (based on analysis)
                # For simplicity, we'll just run it here. Add logic based on analysis later.
                defrag_cmd = [
                    "defrag",
                    f"{target_drive}:",
                    "/U",
                    "/V",
                ]  # Add /O for optimization if needed
                self.logger.info(
                    f"Starting defragmentation for drive {target_drive}: (requires admin)"
                )
                self.logger.debug(f"Running command: {' '.join(defrag_cmd)}")
                defrag_output = subprocess.run(
                    defrag_cmd,
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=3600,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )  # Longer timeout
                self.logger.info(
                    f"Defrag execution output for {target_drive}:\n{defrag_output.stdout}"
                )
                result["details"] = (
                    f"Defragmentation command executed for {target_drive}:. Output logged."
                )
                result["success"] = True  # Assume success if command runs without error

            except subprocess.CalledProcessError as cpe:
                error_msg = f"Defrag command failed for drive {target_drive}: (Requires Admin?). Error: {cpe.stderr or cpe.stdout or cpe}"
                self.logger.error(error_msg)
                result["details"] = error_msg
                raise DiskOperationError(
                    error_msg, {"drive": target_drive, "return_code": cpe.returncode}
                ) from cpe
            except FileNotFoundError:
                error_msg = "defrag.exe not found. Ensure it's in the system PATH."
                self.logger.error(error_msg)
                result["details"] = error_msg
                raise DiskOperationError(error_msg, {"drive": target_drive})
            except subprocess.TimeoutExpired:
                error_msg = f"Defrag command timed out for drive {target_drive}:."
                self.logger.error(error_msg)
                result["details"] = error_msg
                raise DiskOperationError(error_msg, {"drive": target_drive})

            return result

        except Exception as e:
            error_msg = f"Failed to perform disk defragmentation: {e}"
            self.logger.error(error_msg, exc_info=True)
            raise DiskOperationError(error_msg) from e

    def get_disk_usage(self) -> Dict[str, Any]:
        """
        Get disk usage information for all mounted, non-removable drives.

        Returns:
            Dict[str, Any]: Dictionary containing success status, data (disk info),
                            warnings, and inaccessible partition details.

        Raises:
            DiskOperationError: If no accessible disk partitions are found or on critical errors.
        """
        self.logger.debug("Getting disk usage information.")
        disk_info = {}
        inaccessible_partitions = []
        warnings = []
        success = False

        try:
            # all=False attempts to exclude virtual/pseudo filesystems
            # opts='rw' ensures we only look at read-write mounts
            partitions = psutil.disk_partitions(all=False)

            for partition in partitions:
                # Skip potentially problematic types or removable media more explicitly
                # Common problematic types: squashfs, tmpfs (can fill up but often volatile)
                # Check mount options for 'ro' (read-only)
                if (
                    "cdrom" in partition.opts
                    or "ro" in partition.opts
                    or not partition.fstype
                ):
                    self.logger.debug(
                        f"Skipping partition: {partition.device} (Type: {partition.fstype}, Opts: {partition.opts})"
                    )
                    continue

                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    usage_percent = usage.percent
                    status = "healthy"
                    if usage_percent >= 95:
                        status = "critical"
                        warnings.append(
                            f"Critical disk usage ({usage_percent:.1f}%) on {partition.mountpoint} ({partition.device})"
                        )
                    elif usage_percent >= 90:
                        status = "warning"
                        warnings.append(
                            f"High disk usage ({usage_percent:.1f}%) on {partition.mountpoint} ({partition.device})"
                        )

                    disk_info[partition.device] = {
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total_gb": round(usage.total / (1024**3), 2),
                        "used_gb": round(usage.used / (1024**3), 2),
                        "free_gb": round(usage.free / (1024**3), 2),
                        "percent": usage_percent,
                        "status": status,
                    }
                    success = True  # Mark success if at least one partition is read

                except PermissionError:
                    self.logger.warning(
                        f"Permission denied accessing disk usage for {partition.mountpoint}"
                    )
                    inaccessible_partitions.append(
                        {
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "reason": "permission_denied",
                        }
                    )
                except FileNotFoundError:
                    self.logger.warning(
                        f"Mount point not found for {partition.device}: {partition.mountpoint} (possibly disconnected?)"
                    )
                    inaccessible_partitions.append(
                        {
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "reason": "mount_point_not_found",
                        }
                    )
                except OSError as e:
                    # Catch specific OS errors like "[Errno 19] No such device"
                    self.logger.warning(
                        f"OS error getting disk usage for {partition.mountpoint}: {e}"
                    )
                    inaccessible_partitions.append(
                        {
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "reason": f"os_error_{e.errno}",
                        }
                    )
                except Exception as e:
                    # Catch any other unexpected errors for a specific partition
                    self.logger.error(
                        f"Unexpected error getting usage for {partition.mountpoint}: {e}",
                        exc_info=True,
                    )
                    inaccessible_partitions.append(
                        {
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "reason": f"unexpected_{type(e).__name__}",
                        }
                    )

            if not success and not disk_info:
                # Only raise if we couldn't read *any* partition info
                error_details = {
                    "inaccessible_partitions": inaccessible_partitions,
                    "os_type": platform.system(),
                }
                raise DiskOperationError(
                    "No accessible disk partitions found or read successfully.",
                    error_details,
                )

            return {
                "success": True,  # Overall success is true if we could run the function
                "data": disk_info,
                "warnings": warnings,
                "inaccessible": inaccessible_partitions,
            }

        except psutil.Error as e:
            # Catch psutil specific errors during partition listing
            error_msg = f"Failed to list disk partitions: {e}"
            self.logger.error(error_msg, exc_info=True)
            raise DiskOperationError(error_msg, {"error_type": type(e).__name__}) from e
        except Exception as e:
            # Catch unexpected errors during the overall process
            error_msg = f"Failed to get disk usage information: {e}"
            self.logger.error(error_msg, exc_info=True)
            raise DiskOperationError(error_msg, {"error_type": type(e).__name__}) from e

    def manage_startup_programs(
        self, action: str, program_name: str, program_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enable or disable a system startup program (OS-dependent).

        Args:
            action: Action to perform ('enable' or 'disable').
            program_name: The name of the program (used as the registry key/identifier).
            program_path: Full path to the program executable (required for 'enable').

        Returns:
            Dict[str, Any]: Operation result containing success status, details, and error.

        Raises:
            StartupManagementError: If the operation fails or is not supported.
            ValueError: If input parameters are invalid.
        """
        self.logger.info(f"Attempting to {action} startup program: '{program_name}'")
        result = {"success": False, "details": "", "error": None}

        if action not in ("enable", "disable"):
            raise ValueError(
                f"Invalid action '{action}'. Must be 'enable' or 'disable'."
            )
        if not program_name:
            raise ValueError("Program name cannot be empty.")
        if action == "enable" and not program_path:
            raise ValueError("Program path is required for 'enable' action.")
        if action == "enable" and not Path(program_path).is_file():
            raise ValueError(
                f"Program path does not exist or is not a file: {program_path}"
            )

        try:
            if platform.system() == "Windows":
                if not _HAS_WINREG:
                    raise StartupManagementError(
                        "Winreg module not found, cannot manage Windows startup items."
                    )
                op_result = self._manage_windows_startup(
                    action, program_name, program_path
                )
                result.update(op_result)  # Merge results
            elif platform.system() == "Darwin":  # macOS using launchd
                # Requires creating/deleting plist files in ~/Library/LaunchAgents
                # Or using `launchctl` command-line tool
                # This is complex and often requires specific formats.
                raise StartupManagementError(
                    "macOS startup management via launchd not implemented yet."
                )
            elif platform.system() == "Linux":
                # Requires creating/deleting .desktop files in ~/.config/autostart
                raise StartupManagementError(
                    "Linux startup management via autostart not implemented yet."
                )
            else:
                raise StartupManagementError(
                    f"Startup management not supported on this OS: {platform.system()}"
                )

            if result["success"]:
                self.logger.info(
                    f"Successfully {action}d startup program '{program_name}'. Details: {result['details']}"
                )
            else:
                self.logger.error(
                    f"Failed to {action} startup program '{program_name}'. Error: {result['error']}"
                )

            return result

        except ValueError as ve:
            self.logger.error(f"Invalid arguments for managing startup program: {ve}")
            raise  # Re-raise value errors directly
        except Exception as e:
            error_msg = f"Failed to {action} startup program '{program_name}': {e}"
            self.logger.error(error_msg, exc_info=True)
            raise StartupManagementError(
                error_msg, {"action": action, "program": program_name}
            ) from e

    def _manage_windows_startup(
        self, action: str, program_name: str, program_path: Optional[str]
    ) -> Dict[str, Any]:
        """Manage Windows startup programs using the Run registry key."""
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        result = {"success": False, "details": "", "error": None}

        try:
            # Use HKEY_CURRENT_USER for user-specific startup items
            # Use HKEY_LOCAL_MACHINE for system-wide (requires admin)
            # For simplicity, we use HKCU here.
            hkey = winreg.HKEY_CURRENT_USER
            access_mask = winreg.KEY_WRITE | winreg.KEY_READ

            with winreg.OpenKey(hkey, key_path, 0, access_mask) as key:
                if action == "disable":
                    try:
                        # Check if value exists before deleting
                        winreg.QueryValueEx(key, program_name)
                        winreg.DeleteValue(key, program_name)
                        result["success"] = True
                        result["details"] = (
                            f"Disabled startup program '{program_name}'."
                        )
                    except FileNotFoundError:
                        result["success"] = (
                            True  # Considered success if already disabled
                        )
                        result["details"] = (
                            f"Startup program '{program_name}' was already disabled or not found."
                        )
                    except OSError as e:
                        raise StartupManagementError(
                            f"Failed to delete registry value '{program_name}': {e}",
                            {"winerror": e.winerror},
                        ) from e

                elif action == "enable":
                    if not program_path:  # Should be caught earlier, but double-check
                        raise ValueError("Program path is required for enable action.")
                    try:
                        # Use REG_SZ for string path
                        winreg.SetValueEx(
                            key, program_name, 0, winreg.REG_SZ, program_path
                        )
                        result["success"] = True
                        result["details"] = (
                            f"Enabled startup program '{program_name}' with path '{program_path}'."
                        )
                    except OSError as e:
                        raise StartupManagementError(
                            f"Failed to set registry value '{program_name}': {e}",
                            {"winerror": e.winerror},
                        ) from e
        except FileNotFoundError:
            # This means the 'Run' key itself doesn't exist, which is unusual but possible
            error_msg = f"Windows startup registry key not found: HKCU\\{key_path}"
            self.logger.error(error_msg)
            raise StartupManagementError(error_msg)
        except PermissionError:
            error_msg = f"Permission denied accessing Windows startup registry key: HKCU\\{key_path}"
            self.logger.error(error_msg)
            raise StartupManagementError(error_msg)
        except Exception as e:
            # Catch other potential winreg errors
            error_msg = (
                f"Unexpected registry error managing startup item '{program_name}': {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            raise StartupManagementError(error_msg) from e

        return result

    def _cleanup_executor(self) -> bool:
        """Clean up the thread pool executor."""
        if self._executor:
            self.logger.debug("Shutting down thread pool executor.")
            try:
                self._executor.shutdown(
                    wait=True, cancel_futures=True
                )  # Attempt to cancel pending
                self._executor = None
                self.logger.debug("Thread pool executor shut down.")
                return True
            except Exception as e:
                self.logger.error(
                    f"Failed to properly shutdown executor: {e}", exc_info=True
                )
                return False
        return True  # No executor to cleanup

    def _cleanup_tasks(self) -> bool:
        """Perform any necessary cleanup for individual tasks (if defined)."""
        # Currently, tasks don't have specific cleanup, but this structure allows for it.
        self.logger.debug("Performing task cleanup (if any).")
        all_ok = True
        # Example: If tasks held resources, iterate and call task.cleanup()
        # for task_name, task_impl in self._tasks_instances.items():
        #     if hasattr(task_impl, "cleanup"):
        #         try:
        #             task_impl.cleanup()
        #         except Exception as e:
        #             self.logger.error(f"Error cleaning up task {task_name}: {e}")
        #             all_ok = False
        return all_ok

    def cleanup(self) -> bool:
        """
        Clean up resources used by the performance optimizer.

        Ensures graceful shutdown of thread pools and restores settings if necessary.

        Returns:
            bool: True if cleanup was successful, False otherwise.
        """
        self.logger.info("Starting performance optimizer cleanup.")
        self._status = "shutting down"
        all_ok = True

        # 1. Shutdown executor
        if not self._cleanup_executor():
            self.logger.warning("Executor cleanup failed or had issues.")
            all_ok = False  # Mark as not fully clean, but continue

        # 2. Cleanup individual tasks (if needed)
        if not self._cleanup_tasks():
            self.logger.warning("Task cleanup failed or had issues.")
            all_ok = False

        # 3. Restore Windows theme settings if they were modified by a task
        # Check if the 'adjust_windows_theme_performance' task ran with optimize=True
        # This requires tracking task execution details or checking the last run result.
        # Simplified: Always try to restore if original settings exist.
        if platform.system() == "Windows" and self._theme_settings:
            self.logger.info(
                "Attempting to restore original Windows theme settings during cleanup."
            )
            restore_result = self.adjust_windows_theme_performance(
                optimize_for_performance=False
            )
            if not restore_result["success"]:
                self.logger.warning(
                    f"Failed to restore Windows theme settings during cleanup: {restore_result['details']}"
                )
                # Don't mark overall cleanup as failed just for theme restore failure

        # 4. Config saving is handled by ConfigManager externally or on app exit

        self._status = "shutdown"
        if all_ok:
            self.logger.info("Performance optimizer cleanup completed successfully.")
        else:
            self.logger.warning(
                "Performance optimizer cleanup completed with some issues."
            )

        return all_ok
