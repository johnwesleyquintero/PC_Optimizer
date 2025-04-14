from pathlib import Path
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import multiprocessing
import psutil
import platform
import os
import shutil
import datetime
from .base_manager import BasePerformanceOptimizer
from .environment_manager import EnvironmentConfig
from .logging_manager import LoggingManager
import logging


class OptimizationError(Exception):
    """
    Base exception for optimization-related errors.

    Attributes:
        details (Optional[Dict[str, Any]]): Additional details about the error.
    """

    def __init__(
        self,
        message: str = "An optimization error occurred.",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.details = details or {}
        super().__init__(message)


class TaskExecutionError(OptimizationError):
    """
    Exception raised when a specific optimization task fails.

    Attributes:
        task_name (str): The name of the task that failed.
        reason (str): The reason why the task failed.
        details (Optional[Dict[str, Any]]): Additional details about the error.
    """

    def __init__(
        self, task_name: str, reason: str, details: Optional[Dict[str, Any]] = None
    ):
        self.task_name = task_name
        self.reason = reason
        message = f"Task '{task_name}' failed: {reason}"
        super().__init__(message, details)


class MemoryOptimizationError(OptimizationError):
    """
    Exception raised when memory optimization fails.

    Attributes:
        current_usage (float): The current memory usage percentage.
        target_usage (float): The target memory usage percentage.
        details (Optional[Dict[str, Any]]): Additional details about the error.
    """

    def __init__(
        self,
        current_usage: float,
        target_usage: float,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.current_usage = current_usage
        self.target_usage = target_usage
        message = f"Memory optimization failed: Current usage {current_usage}% exceeds target {target_usage}%"
        super().__init__(message, details)


class FileCleanupError(OptimizationError):
    """
    Exception raised when temporary file cleanup fails.

    Attributes:
        path (str): The path where the file cleanup failed.
        error_type (str): The type of error that occurred during file cleanup.
        details (Optional[Dict[str, Any]]): Additional details about the error.
    """

    def __init__(
        self, path: str, error_type: str, details: Optional[Dict[str, Any]] = None
    ):
        self.path = path
        self.error_type = error_type
        message = f"Failed to cleanup files at '{path}': {error_type}"
        super().__init__(message, details)


class PerformanceOptimizer(BasePerformanceOptimizer):
    """
    Manages system performance optimization tasks.

    This class provides methods to initialize, cleanup, and execute
    optimization tasks, as well as retrieve optimization status and
    disk usage information.
    """

    def __init__(self):
        self.config = EnvironmentConfig()
        self.logger = LoggingManager().get_logger(__name__)

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize the performance optimizer.

        Args:
            config: Optional configuration dictionary

        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            self.logger.info("Initializing performance optimizer")
            if config:
                self.config.update(config)
            # Initialize Windows theme performance settings
            if platform.system() == "Windows":
                self._init_windows_theme_performance()
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize performance optimizer: {e}")
            return False

    def _init_windows_theme_performance(self) -> None:
        """Initialize Windows theme-related performance settings."""
        try:
            import winreg

            # Registry keys for Windows theme performance
            theme_keys = {
                "SystemUsesLightTheme": (
                    winreg.HKEY_CURRENT_USER,
                    "Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
                ),
                "AppsUseLightTheme": (
                    winreg.HKEY_CURRENT_USER,
                    "Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
                ),
                "EnableTransparency": (
                    winreg.HKEY_CURRENT_USER,
                    "Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
                ),
            }

            # Store initial theme settings
            self._theme_settings = {}
            for setting, (hkey, path) in theme_keys.items():
                try:
                    with winreg.OpenKey(hkey, path, 0, winreg.KEY_READ) as key:
                        value, _ = winreg.QueryValueEx(key, setting)
                        self._theme_settings[setting] = value
                except WindowsError:
                    self.logger.warning(f"Could not read {setting} from registry")

            self.logger.info("Windows theme performance settings initialized")
        except Exception as e:
            self.logger.error(
                f"Failed to initialize Windows theme performance settings: {e}"
            )
            raise

    def adjust_windows_theme_performance(
        self, optimize_for_performance: bool = True
    ) -> bool:
        """Adjust Windows theme settings for performance.

        Args:
            optimize_for_performance: If True, optimize for performance over aesthetics

        Returns:
            bool: True if adjustments were successful
        """
        if platform.system() != "Windows":
            self.logger.info("Windows theme optimization only available on Windows")
            return False

        try:
            import winreg

            if optimize_for_performance:
                # Disable transparency and use light theme for better performance
                settings = {
                    "SystemUsesLightTheme": 1,  # Use light theme
                    "AppsUseLightTheme": 1,  # Use light theme for apps
                    "EnableTransparency": 0,  # Disable transparency
                }
            else:
                # Restore original settings if available, otherwise use defaults
                settings = (
                    self._theme_settings
                    if hasattr(self, "_theme_settings")
                    else {
                        "SystemUsesLightTheme": 1,
                        "AppsUseLightTheme": 1,
                        "EnableTransparency": 1,
                    }
                )

            for setting, value in settings.items():
                try:
                    key_path = "Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize"
                    with winreg.OpenKey(
                        winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE
                    ) as key:
                        winreg.SetValueEx(key, setting, 0, winreg.REG_DWORD, value)
                except WindowsError as e:
                    self.logger.error(f"Failed to update {setting}: {e}")
                    return False

            self.logger.info(
                f"Windows theme performance settings {'optimized' if optimize_for_performance else 'restored'}"
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to adjust Windows theme performance: {e}")
            return False

    def _cleanup_resources(self) -> bool:
        """Clean up resources used by the optimizer.

        Returns:
            bool: True if cleanup successful, False otherwise
        """
        try:
            self.logger.info("Cleaning up performance optimizer")
            return True
        except Exception as e:
            self.logger.error(f"Failed to cleanup performance optimizer: {e}")
            return False

    def optimize_system(self, profile: Optional[str] = None) -> Dict[str, Any]:
        """Execute system optimization tasks with parallel processing.

        Args:
            profile: Optional optimization profile name from configuration

        Returns:
            Dict containing:
            - success: Overall operation status
            - tasks_completed: Number of successful tasks
            - tasks_failed: List of failed task names with error details

        Raises:
            OptimizationError: If initialization fails
            TaskExecutionError: If any tasks fail during execution
        """
        try:
            self._validate_optimization_ready()
            tasks = self._get_tasks_for_profile(profile)

            with ThreadPoolExecutor(max_workers=self._get_thread_count()) as executor:
                results = self._execute_tasks(executor, tasks)

            return self._generate_optimization_report(results)

        except ValueError as ve:
            error_msg = f"Invalid optimization configuration: {str(ve)}"
            self.logger.error(error_msg)
            raise OptimizationError(error_msg, {"error_type": "configuration"}) from ve
        except TaskExecutionError as te:
            self.logger.error(f"Task execution failed: {te}")
            raise
        except Exception as error:
            error_msg = f"Unexpected error during optimization: {str(error)}"
            self.logger.error(error_msg)
            raise OptimizationError(error_msg, {"error_type": "unexpected"}) from error

    def _validate_optimization_ready(self) -> None:
        """Verify system meets optimization requirements.

        Raises:
            OptimizationError: If configuration is invalid or system requirements not met
        """
        if not self.config.is_valid():
            raise OptimizationError(
                "Invalid configuration detected",
                {"config_state": self.config.get_state()},
            )

        if not self._check_system_resources():
            raise OptimizationError("Insufficient system resources for optimization")

        if self.config.theme == "dark":
            self._apply_dark_mode_performance()

    def _check_system_resources(self) -> bool:
        """Check if system has sufficient resources for optimization.

        Returns:
            bool: True if system meets minimum requirements, False otherwise
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()

            return (
                cpu_percent < 90
                and memory.percent < 95
                and memory.available >= 512 * 1024 * 1024
            )  # 512MB minimum
        except Exception as e:
            self.logger.warning(f"Failed to check system resources: {e}")
            return True  # Assume resources are sufficient if check fails

    def _get_thread_count(self) -> int:
        """Determine optimal thread count for task execution based on system resources.

        Returns:
            int: Optimal number of threads to use for parallel task execution
        """
        cpu_count = multiprocessing.cpu_count()
        memory_available = psutil.virtual_memory().available / (
            1024 * 1024 * 1024
        )  # GB

        # Base thread count on CPU cores and available memory
        suggested_threads = min(
            cpu_count,
            max(1, int(memory_available / 0.5)),  # Assume each thread needs ~0.5GB
        )

        # Apply configuration limits
        return min(
            suggested_threads,
            self.config.max_threads or cpu_count,
            self.config.max_parallel_tasks or float("inf"),
        )

    def _execute_tasks(
        self, executor: ThreadPoolExecutor, tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Execute optimization tasks in parallel with proper error handling.

        Args:
            executor: ThreadPoolExecutor instance for parallel execution
            tasks: List of task configurations to execute

        Returns:
            List[Dict[str, Any]]: Results of task execution

        Raises:
            TaskExecutionError: If critical tasks fail during execution
        """
        futures = {}
        results = []

        # Submit tasks in priority order
        sorted_tasks = sorted(tasks, key=lambda x: x.get("priority", 999))
        for task in sorted_tasks:
            future = executor.submit(self._optimize_task, task)
            futures[future] = task["name"]

        # Collect results with timeout
        for future in concurrent.futures.as_completed(futures.keys()):
            task_name = futures[future]
            try:
                result = future.result(timeout=300)  # 5 minute timeout per task
                results.append(result)
            except concurrent.futures.TimeoutError:
                self.logger.error(f"Task {task_name} timed out")
                results.append(
                    {"name": task_name, "success": False, "error": "timeout"}
                )
            except Exception as e:
                self.logger.error(f"Task {task_name} failed: {e}")
                results.append({"name": task_name, "success": False, "error": str(e)})

        return results

    def _generate_optimization_report(
        self, results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate detailed optimization report with task statistics.

        Args:
            results: List of task execution results

        Returns:
            Dict[str, Any]: Detailed optimization report

        Raises:
            TaskExecutionError: If critical tasks failed during optimization
        """
        failed_tasks = []
        critical_failures = []
        warnings = []

        for result in results:
            if not result.get("success", False):
                task_info = {
                    "name": result["name"],
                    "error": result.get("error", "Unknown error"),
                    }

                if result.get("critical", False):
                    critical_failures.append(task_info)
                else:
                    failed_tasks.append(task_info)

                if result.get("warning"):
                    warnings.append(result["warning"])

        if critical_failures:
            raise TaskExecutionError(
                f"Critical tasks failed: {', '.join(t['name'] for t in critical_failures)}",
                "Critical optimization tasks failed",
                {"critical_failures": critical_failures},
            )

        return {
            "success": len(failed_tasks) == 0,
            "tasks_completed": len(results) - len(failed_tasks),
            "tasks_failed": len(failed_tasks),
            "failed_tasks": failed_tasks,
            "warnings": warnings,
            "timestamp": datetime.datetime.now().isoformat(),
        }

    def get_optimization_status(self) -> Dict[str, Any]:
        """Get current optimization status.

        Returns:
            Dict containing optimization status
        """
        try:
            return {
                "success": True,
                "status": "idle",  # or "running", "completed", "failed"
                "last_run": None,  # timestamp of last optimization
                "current_task": None,  # current running task if any
            }
        except Exception as e:
            self.logger.error(f"Failed to get optimization status: {e}")
            return {"success": False, "error": str(e)}

    def _apply_dark_mode_performance(self):
        # Windows-specific dark mode optimizations
        pass

    def _cleanup_executor(self) -> bool:
        """Clean up thread pool executor resources.

        Returns:
            bool: True if cleanup was successful, False otherwise
        """
        try:
            if hasattr(self, "_executor") and self._executor:
                self._executor.shutdown(wait=True)
            return True
        except Exception as e:
            self.logger.error(f"Failed to cleanup executor: {e}")
            return False

    def _adjust_windows_theme_performance(self):
        # Placeholder for Windows theme perf. adjustments
        pass

    def get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage information for all drives.

        Returns:
            Dict[str, Any]: Dictionary containing disk usage information for each drive
                with total, used, free space and usage percentage.

        Raises:
            OptimizationError: If no accessible disk partitions are found or on critical errors
        """
        try:
            disk_info = {}
            inaccessible_partitions = []

            for partition in psutil.disk_partitions(all=False):
                if not partition.fstype:
                    continue

                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info[partition.device] = {
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": usage.percent,
                        "status": "healthy" if usage.percent < 90 else "warning",
                    }
                except PermissionError:
                    inaccessible_partitions.append(
                        {
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "reason": "permission_denied",
                        }
                    )
                    continue
                except OSError as e:
                    inaccessible_partitions.append(
                        {
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "reason": str(e),
                        }
                    )
                    continue

            if not disk_info:
                error_details = {
                    "inaccessible_partitions": inaccessible_partitions,
                    "os_type": platform.system(),
                }
                raise OptimizationError(
                    "No accessible disk partitions found", error_details
                )

            return {
                "success": True,
                "data": disk_info,
                "warnings": [
                    f"Warning: High disk usage ({info['percent']}%) on {device}"
                    for device, info in disk_info.items()
                    if info["percent"] >= 90
                ],
                "inaccessible": inaccessible_partitions,
            }

        except OptimizationError:
            raise
        except Exception as e:
            error_msg = f"Failed to get disk usage information: {str(e)}"
            self.logger.error(error_msg)
            raise OptimizationError(
                error_msg,
                {"error_type": type(e).__name__, "os_type": platform.system()},
            ) from e

    def manage_startup_programs(
        self, action: str, program: Dict[str, str]
    ) -> Dict[str, Any]:
        """Manage system startup programs.

        Args:
            action: Action to perform ('enable' or 'disable')
            program: Program information dictionary containing:
                - name: Program display name
                - path: Full path to the program executable
                - description: Optional program description

        Returns:
            Dict[str, Any]: Operation result containing:
                - success: Boolean indicating operation success
                - error: Error message if operation failed
                - details: Additional operation details

        Raises:
            OptimizationError: If the operation fails or is not supported
        """
        if action not in ("enable", "disable"):
            raise ValueError(
                f"Invalid action '{action}'. Must be 'enable' or 'disable'"
            )

        if not isinstance(program, dict) or "name" not in program:
            raise ValueError("Program must be a dictionary containing 'name'")

        if action == "enable" and "path" not in program:
            raise ValueError("Program path required for 'enable' action")

        try:
            if platform.system() == "Windows":
                return self._manage_windows_startup(action, program)
            else:
                raise OptimizationError(
                    "Startup management not supported on this OS",
                    {"os_type": platform.system()},
                )

        except Exception as e:
            error_msg = (
                f"Failed to {action} startup program '{program.get('name', 'unknown')}'"
            )
            self.logger.error(f"{error_msg}: {e}")
            raise OptimizationError(
                error_msg,
                {
                    "action": action,
                    "program": program.get("name"),
                    "error_type": type(e).__name__,
                },
            ) from e

    def _manage_windows_startup(
        self, action: str, program: Dict[str, str]
    ) -> Dict[str, Any]:
        """Manage Windows startup programs using registry.

        Args:
            action: Action to perform ('enable' or 'disable')
            program: Program information dictionary

        Returns:
            Dict[str, Any]: Operation result

        Raises:
            WindowsError: If registry operation fails
        """
        import winreg

        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        program_name = program["name"]

        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS
            ) as key:
                if action == "disable":
                    try:
                        winreg.DeleteValue(key, program_name)
                    except WindowsError as e:
                        if e.winerror == 2:  # ERROR_FILE_NOT_FOUND
                            return {
                                "success": True,
                                "details": "Program was not in startup",
                            }
                        raise
                else:  # enable
                    winreg.SetValueEx(
                        key, program_name, 0, winreg.REG_SZ, program["path"]
                    )

            return {
                "success": True,
                "details": f"Successfully {action}d {program_name}",
            }

        except WindowsError as e:
            return {
                "success": False,
                "error": f"Registry operation failed: {e}",
                "error_code": e.winerror,
            }

    def _get_tasks(self, profile: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of optimization tasks to perform based on profile.

        Args:
            profile: Optional optimization profile name

        Returns:
            List[Dict[str, Any]]: List of task configurations with priorities

        Raises:
            OptimizationError: If profile is invalid or tasks cannot be loaded
        """
        try:
            # Load tasks based on profile or use defaults
            if profile:
                tasks = self._load_profile_tasks(profile)
            else:
                tasks = [
                    {
                        "name": "memory_optimization",
                        "function": self.adjust_memory_usage,
                        "priority": 1,
                        "critical": True,
                        "timeout": 300,  # 5 minutes
                    },
                    {
                        "name": "temp_cleanup",
                        "function": self.clean_temp_files,
                        "priority": 2,
                        "critical": False,
                        "timeout": 600,  # 10 minutes
                    },
                    {
                        "name": "disk_optimization",
                        "function": self.optimize_disk_usage,
                        "priority": 3,
                        "critical": False,
                        "timeout": 1800,  # 30 minutes
                    },
                ]

            # Validate task configurations
            for task in tasks:
                if not all(k in task for k in ("name", "function", "priority")):
                    raise OptimizationError(
                        f"Invalid task configuration for {task.get('name', 'unknown')}",
                        {"task": task},
                    )

            return sorted(tasks, key=lambda x: x["priority"])

        except Exception as e:
            error_msg = f"Failed to load optimization tasks: {str(e)}"
            self.logger.error(error_msg)
            raise OptimizationError(
                error_msg, {"profile": profile, "error_type": type(e).__name__}
            ) from e
        return sorted(tasks, key=lambda x: x["priority"])

    def _optimize_task(self, task: Dict[str, Any]) -> bool:
        """Execute a single optimization task.

        Args:
            task (Dict[str, Any]): Task configuration

        Returns:
            bool: True if task completed successfully, False otherwise
        """
        try:
            logging.info(f"_optimize_task: Starting task {task['name']}")
            result = task["function"]()
            logging.info(f"_optimize_task: Completed task {task['name']}")
            return result
        except Exception as e:
            logging.error(f"_optimize_task: Failed to execute task {task['name']}: {e}")
            return False

    def adjust_memory_usage(self) -> bool:
        """Adjust system memory usage based on available memory using centralized configuration.

        This function uses a centralized configuration approach to manage memory thresholds
        and corresponding system adjustments. The configuration includes:
        - Memory thresholds for different usage levels
        - Thread count adjustments for each level
        - Process priority adjustments
        - Cache clearing triggers

        Returns:
            bool: True if adjustment was successful, False otherwise.

        Raises:
            MemoryOptimizationError: If memory adjustment fails.
        """
        try:
            self.logger.info("Adjusting memory usage using centralized configuration")
            system_memory = psutil.virtual_memory()

            # Load memory management configuration
            memory_config = {
                "critical": {
                    "windows": {
                        "gc_collect": True
                    }
                }
            }
            
            # On Windows, we can suggest garbage collection
            import gc
            gc.collect()
            
            # Clear disk cache using built-in tools
            os.system('powershell -Command "Clear-DnsClientCache"')
            os.system('powershell -Command "Clear-BCCache -Force"')

            self.logger.info("System cache cleared successfully")
        except Exception as e:
            self.logger.warning(f"Failed to clear system cache: {e}")

    def get_log_path(self) -> Path:
        """Get the path for optimization logs.

        Returns:
            Path: Path to the log file
        """
        log_path = (
            self.config.output_dir / "optimization_logs" / f"{platform.node()}.log"
        )
        log_path.parent.mkdir(parents=True, exist_ok=True)
        return log_path

    def clean_temp_files(self) -> Dict[str, Any]:
        """Clean temporary files from system temporary directories using a targeted approach.

        The function uses the following strategies:
        1. Checks disk space and adjusts cleanup aggressiveness
        2. Targets specific file types based on age and size
        3. Preserves important system temp files
        4. Uses a gradual cleanup approach based on file age

        Returns:
            Dict[str, Any]: Cleanup operation results including success status,
                          files removed count and any errors encountered

        Raises:
            FileCleanupError: If cleanup process encounters critical errors or disk space check fails.
        """
        try:
            # Check disk space before cleaning
            temp_path = os.environ.get(
                "TEMP", os.path.expanduser("~\\AppData\\Local\\Temp")
            )
            total, used, free = shutil.disk_usage(temp_path)
            free_gb = free / (1024 * 1024 * 1024)  # Convert to GB
            used_percent = (used / total) * 100

            self.logger.info(
                f"Disk space check - Free: {free_gb:.2f}GB, Used: {used_percent:.1f}%"
            )

            # Define cleanup thresholds based on disk usage
            if used_percent > 90:
                age_threshold = 1  # 1 day for critical disk usage
                self.logger.warning(
                    f"Disk usage critical at {used_percent:.1f}%. Using aggressive cleanup."
                )
            elif used_percent > 75:
                age_threshold = 7  # 7 days for high disk usage
                self.logger.info(
                    f"Disk usage high at {used_percent:.1f}%. Using standard cleanup."
                )
            else:
                age_threshold = 30  # 30 days for normal disk usage
                self.logger.info(
                    f"Disk usage normal at {used_percent:.1f}%. Using conservative cleanup."
                )

            # Define file patterns to clean based on extension
            cleanup_patterns = {
                "temp_files": ["*.tmp", "*.temp", "~*", "*.bak", "*.old"],
                "log_files": ["*.log", "*.log.*", "*.dmp"],
                "cache_files": ["*.cache", "*.chk", "*.nch"],
                "download_artifacts": ["*.crdownload", "*.part", "*.download"],
            }

            # Get all possible temp directories
            temp_dirs = []
            for env_var in ["TEMP", "TMP"]:
                if path := os.environ.get(env_var):
                    temp_dirs.append(Path(path))

            if not temp_dirs:
                temp_dirs.append(
                    Path(os.environ["USERPROFILE"]) / "AppData" / "Local" / "Temp"
                )

            cleaned_files_count = 0
            preserved_files_count = 0
            errors = []

            import time

            current_time = time.time()

            for temp_dir in temp_dirs:
                if not temp_dir.is_dir():
                    continue

                self.logger.info(f"Cleaning temporary files from: {temp_dir}")
                try:
                    for pattern_type, patterns in cleanup_patterns.items():
                        for pattern in patterns:
                            try:
                                for item in temp_dir.glob(pattern):
                                    try:
                                        # Check file age
                                        file_age_days = (
                                            current_time - item.stat().st_mtime
                                        ) / (24 * 3600)

                                        # Skip system files and recent files
                                        if (
                                            item.name.startswith("sys")
                                            or file_age_days < age_threshold
                                        ):
                                            preserved_files_count += 1
                                            continue

                                        if item.is_file() or item.is_symlink():
                                            item.unlink(missing_ok=True)
                                            cleaned_files_count += 1
                                            self.logger.debug(
                                                f"Removed {pattern_type}: {item}"
                                            )
                                        elif item.is_dir():
                                            shutil.rmtree(item, ignore_errors=True)
                                            cleaned_files_count += 1
                                            self.logger.debug(
                                                f"Removed directory: {item}"
                                            )
                                    except PermissionError as e:
                                        errors.append(
                                            {
                                                "path": str(item),
                                                "error": f"Permission denied: {str(e)}",
                                            }
                                        )
                                        self.logger.debug(
                                            f"Permission denied for {item}: {str(e)}"
                                        )
                                    except OSError as e:
                                        errors.append(
                                            {"path": str(item), "error": str(e)}
                                        )
                                        self.logger.warning(
                                            f"Failed to remove {item}: {str(e)}"
                                        )
                            except Exception as e:
                                self.logger.warning(
                                    f"Error processing pattern {pattern}: {str(e)}"
                                )
                except Exception as e:
                    error_msg = f"Critical error while cleaning {temp_dir}: {str(e)}"
                    self.logger.error(error_msg)
                    raise FileCleanupError(str(temp_dir), error_msg)

            return {
                "success": len(errors) == 0,
                "files_removed": cleaned_files_count,
                "files_preserved": preserved_files_count,
                "disk_usage_percent": used_percent,
                "free_space_gb": free_gb,
                "errors": errors,
            }
        except Exception as e:
            error_msg = f"Failed to clean temporary files: {str(e)}"
            self.logger.error(error_msg)
            raise FileCleanupError(temp_path, error_msg)

    def _cleanup_tasks(self) -> bool:
        """Clean up task resources.

        Returns:
            bool: True if cleanup was successful, False otherwise
        """
        try:
            if not hasattr(self, "_tasks") or not self._tasks:
                return True
            
            for task in self._tasks:
                if hasattr(task, "cleanup") and callable(task.cleanup):
                    task.cleanup()
            return True
        except Exception as e:
            self.logger.error(f"Failed to cleanup tasks: {e}")
            return False

    def cleanup(self) -> bool:
        """Clean up resources and perform graceful shutdown.

        This method ensures proper cleanup of resources including thread pools,
        system handles, and tasks before shutdown.

        Returns:
            bool: True if cleanup was successful, False otherwise
        """
        try:
            self.logger.info("Starting performance optimizer cleanup")
            
            # Clean up executor and tasks
            executor_ok = self._cleanup_executor()
            tasks_ok = self._cleanup_tasks()
            
            # Save pending configuration changes
            self.config.save_config()

            # Adjust Windows theme performance if needed
            if self.config.system == "Windows":
                self._adjust_windows_theme_performance()

            cleanup_ok = executor_ok and tasks_ok
            if cleanup_ok:
                self.logger.info("Performance optimizer cleanup completed")
            return cleanup_ok
        except Exception as e:
            self.logger.error(f"Failed to cleanup optimizer: {e}")
            return False

    def _adjust_windows_theme_performance(self):
        # Placeholder for Windows theme perf. adjustments
        pass

    def get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage information for all drives.

        Returns:
            Dict[str, Any]: Dictionary containing disk usage information for each drive
                with total, used, free space and usage percentage.

        Raises:
            OptimizationError: If no accessible disk partitions are found or on critical errors
        """
        try:
            disk_info = {}
            inaccessible_partitions = []

            for partition in psutil.disk_partitions(all=False):
                if not partition.fstype:
                    continue

                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info[partition.device] = {
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": usage.percent,
                        "status": "healthy" if usage.percent < 90 else "warning",
                    }
                except PermissionError:
                    inaccessible_partitions.append(
                        {
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "reason": "permission_denied",
                        }
                    )
                    continue
                except OSError as e:
                    inaccessible_partitions.append(
                        {
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "reason": str(e),
                        }
                    )
                    continue

            if not disk_info:
                error_details = {
                    "inaccessible_partitions": inaccessible_partitions,
                    "os_type": platform.system(),
                }
                raise OptimizationError(
                    "No accessible disk partitions found", error_details
                )

            return {
                "success": True,
                "data": disk_info,
                "warnings": [
                    f"Warning: High disk usage ({info['percent']}%) on {device}"
                    for device, info in disk_info.items()
                    if info["percent"] >= 90
                ],
                "inaccessible": inaccessible_partitions,
            }

        except OptimizationError:
            raise
        except Exception as e:
            error_msg = f"Failed to get disk usage information: {str(e)}"
            self.logger.error(error_msg)
            raise OptimizationError(
                error_msg,
                {"error_type": type(e).__name__, "os_type": platform.system()},
            ) from e

    def manage_startup_programs(
        self, action: str, program: Dict[str, str]
    ) -> Dict[str, Any]:
        """Manage system startup programs.

        Args:
            action: Action to perform ('enable' or 'disable')
            program: Program information dictionary containing:
                - name: Program display name
                - path: Full path to the program executable
                - description: Optional program description

        Returns:
            Dict[str, Any]: Operation result containing:
                - success: Boolean indicating operation success
                - error: Error message if operation failed
                - details: Additional operation details

        Raises:
            OptimizationError: If the operation fails or is not supported
        """
        if action not in ("enable", "disable"):
            raise ValueError(
                f"Invalid action '{action}'. Must be 'enable' or 'disable'"
            )

        if not isinstance(program, dict) or "name" not in program:
            raise ValueError("Program must be a dictionary containing 'name'")

        if action == "enable" and "path" not in program:
            raise ValueError("Program path required for 'enable' action")

        try:
            if platform.system() == "Windows":
                return self._manage_windows_startup(action, program)
            else:
                raise OptimizationError(
                    "Startup management not supported on this OS",
                    {"os_type": platform.system()},
                )

        except Exception as e:
            error_msg = (
                f"Failed to {action} startup program '{program.get('name', 'unknown')}'"
            )
            self.logger.error(f"{error_msg}: {e}")
            raise OptimizationError(
                error_msg,
                {
                    "action": action,
                    "program": program.get("name"),
                    "error_type": type(e).__name__,
                },
            ) from e

    def _manage_windows_startup(
        self, action: str, program: Dict[str, str]
    ) -> Dict[str, Any]:
        """Manage Windows startup programs using registry.

        Args:
            action: Action to perform ('enable' or 'disable')
            program: Program information dictionary

        Returns:
            Dict[str, Any]: Operation result

        Raises:
            WindowsError: If registry operation fails
        """
        import winreg

        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        program_name = program["name"]

        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS
            ) as key:
                if action == "disable":
                    try:
                        winreg.DeleteValue(key, program_name)
                    except WindowsError as e:
                        if e.winerror == 2:  # ERROR_FILE_NOT_FOUND
                            return {
                                "success": True,
                                "details": "Program was not in startup",
                            }
                        raise
                else:  # enable
                    winreg.SetValueEx(
                        key, program_name, 0, winreg.REG_SZ, program["path"]
                    )

            return {
                "success": True,
                "details": f"Successfully {action}d {program_name}",
            }

        except WindowsError as e:
            return {
                "success": False,
                "error": f"Registry operation failed: {e}",
                "error_code": e.winerror,
            }

    def _get_tasks(self, profile: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of optimization tasks to perform based on profile.

        Args:
            profile: Optional optimization profile name

        Returns:
            List[Dict[str, Any]]: List of task configurations with priorities

        Raises:
            OptimizationError: If profile is invalid or tasks cannot be loaded
        """
        try:
            # Load tasks based on profile or use defaults
            if profile:
                tasks = self._load_profile_tasks(profile)
            else:
                tasks = [
                    {
                        "name": "memory_optimization",
                        "function": self.adjust_memory_usage,
                        "priority": 1,
                        "critical": True,
                        "timeout": 300,  # 5 minutes
                    },
                    {
                        "name": "temp_cleanup",
                        "function": self.clean_temp_files,
                        "priority": 2,
                        "critical": False,
                        "timeout": 600,  # 10 minutes
                    },
                    {
                        "name": "disk_optimization",
                        "function": self.optimize_disk_usage,
                        "priority": 3,
                        "critical": False,
                        "timeout": 1800,  # 30 minutes
                    },
                ]

            # Validate task configurations
            for task in tasks:
                if not all(k in task for k in ("name", "function", "priority")):
                    raise OptimizationError(
                        f"Invalid task configuration for {task.get('name', 'unknown')}",
                        {"task": task},
                    )

            return sorted(tasks, key=lambda x: x["priority"])

        except Exception as e:
            error_msg = f"Failed to load optimization tasks: {str(e)}"
            self.logger.error(error_msg)
            raise OptimizationError(
                error_msg, {"profile": profile, "error_type": type(e).__name__}
            ) from e
        return sorted(tasks, key=lambda x: x["priority"])

    def _optimize_task(self, task: Dict[str, Any]) -> bool:
        """Execute a single optimization task.

        Args:
            task (Dict[str, Any]): Task configuration

        Returns:
            bool: True if task completed successfully, False otherwise
        """
        try:
            logging.info(f"_optimize_task: Starting task {task['name']}")
            result = task["function"]()
            logging.info(f"_optimize_task: Completed task {task['name']}")
            return result
        except Exception as e:
            logging.error(f"_optimize_task: Failed to execute task {task['name']}: {e}")
            return False

    def adjust_memory_usage(self) -> bool:
        """Adjust system memory usage based on available memory using centralized configuration.

        This function uses a centralized configuration approach to manage memory thresholds
        and corresponding system adjustments. The configuration includes:
        - Memory thresholds for different usage levels
        - Thread count adjustments for each level
        - Process priority adjustments
        - Cache clearing triggers

        Returns:
            bool: True if adjustment was successful, False otherwise.

        Raises:
            MemoryOptimizationError: If memory adjustment fails.
        """
        try:
            self.logger.info("Adjusting memory usage using centralized configuration")
            system_memory = psutil.virtual_memory()

            # Load memory management configuration
            memory_config = {
                "critical": {
                    "threshold": 2 * 1024**3,  # 2GB
                    "max_threads": 2,
                    "process_priority": psutil.HIGH_PRIORITY_CLASS,
                    "clear_cache": True,
                },
                "warning": {
                    "threshold": 4 * 1024**3,  # 4GB
                    "max_threads": 4,
                    "process_priority": psutil.ABOVE_NORMAL_PRIORITY_CLASS,
                    "clear_cache": True,
                },
                "normal": {
                    "threshold": 8 * 1024**3,  # 8GB
                    "max_threads": 8,
                    "process_priority": psutil.NORMAL_PRIORITY_CLASS,
                    "clear_cache": False,
                },
            }

            # Determine current memory state
            if system_memory.available < memory_config["critical"]["threshold"]:
                current_state = "critical"
            elif system_memory.available < memory_config["warning"]["threshold"]:
                current_state = "warning"
            else:
                current_state = "normal"

            # Apply memory optimizations
            state_config = memory_config[current_state]

            # Update thread configuration
            self.config.config.set(
                "Performance", "max_threads", str(state_config["max_threads"])
            )
            self.config.save_config()

            # Adjust process priority if on Windows
            if platform.system() == "Windows":
                current_process = psutil.Process()
                current_process.nice(state_config["process_priority"])

            # Clear system cache if needed
            if state_config["clear_cache"]:
                self._clear_system_cache()

            self.logger.info(
                f"Memory optimization applied - State: {current_state}, "
                f"Usage: {system_memory.percent}%, "
                f"Threads: {state_config['max_threads']}"
            )

            return True
        except Exception as e:
            error_msg = f"Failed to adjust memory usage: {str(e)}"
            self.logger.error(error_msg)
            raise MemoryOptimizationError(system_memory.percent, 75, {"error": str(e)})

    def _clear_system_cache(self) -> None:
        """Clear system cache to free up memory.

        This is a helper method for memory optimization that attempts to clear
        various system caches depending on the operating system.
        """
        try:
            if platform.system() == "Windows":
                # On Windows, we can suggest garbage collection
                import gc

                gc.collect()

                # Clear disk cache using built-in tools
                os.system('powershell -Command "Clear-DnsClientCache"')
                os.system('powershell -Command "Clear-BCCache -Force"')

            self.logger.info("System cache cleared successfully")
        except Exception as e:
            self.logger.warning(f"Failed to clear system cache: {e}")

    def get_log_path(self) -> Path:
        """Get the path for optimization logs.

        Returns:
            Path: Path to the log file
        """
        log_path = (
            self.config.output_dir / "optimization_logs" / f"{platform.node()}.log"
        )
        log_path.parent.mkdir(parents=True, exist_ok=True)
        return log_path

    def clean_temp_files(self) -> Dict[str, Any]:
        """Clean temporary files from system temporary directories using a targeted approach.

        The function uses the following strategies:
        1. Checks disk space and adjusts cleanup aggressiveness
        2. Targets specific file types based on age and size
        3. Preserves important system temp files
        4. Uses a gradual cleanup approach based on file age

        Returns:
            Dict[str, Any]: Cleanup operation results including success status,
                          files removed count and any errors encountered

        Raises:
            FileCleanupError: If cleanup process encounters critical errors or disk space check fails.
        """
        try:
            # Check disk space before cleaning
            temp_path = os.environ.get(
                "TEMP", os.path.expanduser("~\\AppData\\Local\\Temp")
            )
            total, used, free = shutil.disk_usage(temp_path)
            free_gb = free / (1024 * 1024 * 1024)  # Convert to GB
            used_percent = (used / total) * 100

            self.logger.info(
                f"Disk space check - Free: {free_gb:.2f}GB, Used: {used_percent:.1f}%"
            )

            # Define cleanup thresholds based on disk usage
            if used_percent > 90:
                age_threshold = 1  # 1 day for critical disk usage
                self.logger.warning(
                    f"Disk usage critical at {used_percent:.1f}%. Using aggressive cleanup."
                )
            elif used_percent > 75:
                age_threshold = 7  # 7 days for high disk usage
                self.logger.info(
                    f"Disk usage high at {used_percent:.1f}%. Using standard cleanup."
                )
            else:
                age_threshold = 30  # 30 days for normal disk usage
                self.logger.info(
                    f"Disk usage normal at {used_percent:.1f}%. Using conservative cleanup."
                )

            # Define file patterns to clean based on extension
            cleanup_patterns = {
                "temp_files": ["*.tmp", "*.temp", "~*", "*.bak", "*.old"],
                "log_files": ["*.log", "*.log.*", "*.dmp"],
                "cache_files": ["*.cache", "*.chk", "*.nch"],
                "download_artifacts": ["*.crdownload", "*.part", "*.download"],
            }

            # Get all possible temp directories
            temp_dirs = []
            for env_var in ["TEMP", "TMP"]:
                if path := os.environ.get(env_var):
                    temp_dirs.append(Path(path))

            if not temp_dirs:
                temp_dirs.append(
                    Path(os.environ["USERPROFILE"]) / "AppData" / "Local" / "Temp"
                )

            cleaned_files_count = 0
            preserved_files_count = 0
            errors = []

            import time

            current_time = time.time()

            for temp_dir in temp_dirs:
                if not temp_dir.is_dir():
                    continue

                self.logger.info(f"Cleaning temporary files from: {temp_dir}")
                try:
                    for pattern_type, patterns in cleanup_patterns.items():
                        for pattern in patterns:
                            try:
                                for item in temp_dir.glob(pattern):
                                    try:
                                        # Check file age
                                        file_age_days = (
                                            current_time - item.stat().st_mtime
                                        ) / (24 * 3600)

                                        # Skip system files and recent files
                                        if (
                                            item.name.startswith("sys")
                                            or file_age_days < age_threshold
                                        ):
                                            preserved_files_count += 1
                                            continue

                                        if item.is_file() or item.is_symlink():
                                            item.unlink(missing_ok=True)
                                            cleaned_files_count += 1
                                            self.logger.debug(
                                                f"Removed {pattern_type}: {item}"
                                            )
                                        elif item.is_dir():
                                            shutil.rmtree(item, ignore_errors=True)
                                            cleaned_files_count += 1
                                            self.logger.debug(
                                                f"Removed directory: {item}"
                                            )
                                    except PermissionError as e:
                                        errors.append(
                                            {
                                                "path": str(item),
                                                "error": f"Permission denied: {str(e)}",
                                            }
                                        )
                                        self.logger.debug(
                                            f"Permission denied for {item}: {str(e)}"
                                        )
                                    except OSError as e:
                                        errors.append(
                                            {"path": str(item), "error": str(e)}
                                        )
                                        self.logger.warning(
                                            f"Failed to remove {item}: {str(e)}"
                                        )
                            except Exception as e:
                                self.logger.warning(
                                    f"Error processing pattern {pattern}: {str(e)}"
                                )
                except Exception as e:
                    error_msg = f"Critical error while cleaning {temp_dir}: {str(e)}"
                    self.logger.error(error_msg)
                    raise FileCleanupError(str(temp_dir), error_msg)

            return {
                "success": len(errors) == 0,
                "files_removed": cleaned_files_count,
                "files_preserved": preserved_files_count,
                "disk_usage_percent": used_percent,
                "free_space_gb": free_gb,
                "errors": errors,
            }
        except Exception as e:
            error_msg = f"Failed to clean temporary files: {str(e)}"
            self.logger.error(error_msg)
            raise FileCleanupError(temp_path, error_msg)

    def _cleanup_tasks(self) -> bool:
        """Clean up task resources.

        Returns:
            bool: True if cleanup was successful, False otherwise
        """
        try:
            if not hasattr(self, "_tasks") or not self._tasks:
                return True
            
            for task in self._tasks:
                if hasattr(task, "cleanup") and callable(task.cleanup):
                    task.cleanup()
            return True
        except Exception as e:
            self.logger.error(f"Failed to cleanup tasks: {e}")
            return False

    def cleanup(self) -> bool:
        """Clean up resources and perform graceful shutdown.

        This method ensures proper cleanup of resources including thread pools,
        system handles, and tasks before shutdown.

        Returns:
            bool: True if cleanup was successful, False otherwise
        """
        try:
            self.logger.info("Starting performance optimizer cleanup")
            
            # Clean up executor and tasks
            executor_ok = self._cleanup_executor()
            tasks_ok = self._cleanup_tasks()
            
            # Save pending configuration changes
            self.config.save_config()

            # Adjust Windows theme performance if needed
            if self.config.system == "Windows":
                self._adjust_windows_theme_performance()

            cleanup_ok = executor_ok and tasks_ok
            if cleanup_ok:
                self.logger.info("Performance optimizer cleanup completed")
            return cleanup_ok
        except Exception as e:
            self.logger.error(f"Failed to cleanup optimizer: {e}")
            return False

    def _adjust_windows_theme_performance(self):
        # Placeholder for Windows theme perf. adjustments
        pass

    def get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage information for all drives.

        Returns:
            Dict[str, Any]: Dictionary containing disk usage information for each drive
                with total, used, free space and usage percentage.

        Raises:
            OptimizationError: If no accessible disk partitions are found or on critical errors
        """
        try:
            disk_info = {}
            inaccessible_partitions = []

            for partition in psutil.disk_partitions(all=False):
                if not partition.fstype:
                    continue

                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info[partition.device] = {
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": usage.percent,
                        "status": "healthy" if usage.percent < 90 else "warning",
                    }
                except PermissionError:
                    inaccessible_partitions.append(
                        {
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "reason": "permission_denied",
                        }
                    )
                    continue
                except OSError as e:
                    inaccessible_partitions.append(
                        {
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "reason": str(e),
                        }
                    )
                    continue

            if not disk_info:
                error_details = {
                    "inaccessible_partitions": inaccessible_partitions,
                    "os_type": platform.system(),
                }
                raise OptimizationError(
                    "No accessible disk partitions found", error_details
                )

            return {
                "success": True,
                "data": disk_info,
                "warnings": [
                    f"Warning: High disk usage ({info['percent']}%) on {device}"
                    for device, info in disk_info.items()
                    if info["percent"] >= 90
                ],
                "inaccessible": inaccessible_partitions,
            }

        except OptimizationError:
            raise
        except Exception as e:
            error_msg = f"Failed to get disk usage information: {str(e)}"
            self.logger.error(error_msg)
            raise OptimizationError(
                error_msg,
                {"error_type": type(e).__name__, "os_type": platform.system()},
            ) from e

    def manage_startup_programs(
        self, action: str, program: Dict[str, str]
    ) -> Dict[str, Any]:
        """Manage system startup programs.

        Args:
            action: Action to perform ('enable' or 'disable')
            program: Program information dictionary containing:
                - name: Program display name
                - path: Full path to the program executable
                - description: Optional program description

        Returns:
            Dict[str, Any]: Operation result containing:
                - success: Boolean indicating operation success
                - error: Error message if operation failed
                - details: Additional operation details

        Raises:
            OptimizationError: If the operation fails or is not supported
        """
        if action not in ("enable", "disable"):
            raise ValueError(
                f"Invalid action '{action}'. Must be 'enable' or 'disable'"
            )

        if not isinstance(program, dict) or "name" not in program:
            raise ValueError("Program must be a dictionary containing 'name'")

        if action == "enable" and "path" not in program:
            raise ValueError("Program path required for 'enable' action")

        try:
            if platform.system() == "Windows":
                return self._manage_windows_startup(action, program)
            else:
                raise OptimizationError(
                    "Startup management not supported on this OS",
                    {"os_type": platform.system()},
                )

        except Exception as e:
            error_msg = (
                f"Failed to {action} startup program '{program.get('name', 'unknown')}'"
            )
            self.logger.error(f"{error_msg}: {e}")
            raise OptimizationError(
                error_msg,
                {
                    "action": action,
                    "program": program.get("name"),
                    "error_type": type(e).__name__,
                },
            ) from e

    def _manage_windows_startup(
        self, action: str, program: Dict[str, str]
    ) -> Dict[str, Any]:
        """Manage Windows startup programs using registry.

        Args:
            action: Action to perform ('enable' or 'disable')
            program: Program information dictionary

        Returns:
            Dict[str, Any]: Operation result

        Raises:
            WindowsError: If registry operation fails
        """
        import winreg

        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        program_name = program["name"]

        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS
            ) as key:
                if action == "disable":
                    try:
                        winreg.DeleteValue(key, program_name)
                    except WindowsError as e:
                        if e.winerror == 2:  # ERROR_FILE_NOT_FOUND
                            return {
                                "success": True,
                                "details": "Program was not in startup",
                            }
                        raise
                else:  # enable
                    winreg.SetValueEx(
                        key, program_name, 0, winreg.REG_SZ, program["path"]
                    )

            return {
                "success": True,
                "details": f"Successfully {action}d {program_name}",
            }

        except WindowsError as e:
            return {
                "success": False,
                "error": f"Registry operation failed: {e}",
                "error_code": e.winerror,
            }

    def _get_tasks(self, profile: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of optimization tasks to perform based on profile.

        Args:
            profile: Optional optimization profile name

        Returns:
            List[Dict[str, Any]]: List of task configurations with priorities

        Raises:
            OptimizationError: If profile is invalid or tasks cannot be loaded
        """
        try:
            # Load tasks based on profile or use defaults
            if profile:
                tasks = self._load_profile_tasks(profile)
            else:
                tasks = [
                    {
                        "name": "memory_optimization",
                        "function": self.adjust_memory_usage,
                        "priority": 1,
                        "critical": True,
                        "timeout": 300,  # 5 minutes
                    },
                    {
                        "name": "temp_cleanup",
                        "function": self.clean_temp_files,
                        "priority": 2,
                        "critical": False,
                        "timeout": 600,  # 10 minutes
                    },
                    {
                        "name": "disk_optimization",
                        "function": self.optimize_disk_usage,
                        "priority": 3,
                        "critical": False,
                        "timeout": 1800,  # 30 minutes
                    },
                ]

            # Validate task configurations
            for task in tasks:
                if not all(k in task for k in ("name", "function", "priority")):
                    raise OptimizationError(
                        f"Invalid task configuration for {task.get('name', 'unknown')}",
                        {"task": task},
                    )

            return sorted(tasks, key=lambda x: x["priority"])

        except Exception as e:
            error_msg = f"Failed to load optimization tasks: {str(e)}"
            self.logger.error(error_msg)
            raise OptimizationError(
                error_msg, {"profile": profile, "error_type": type(e).__name__}
            ) from e
        return sorted(tasks, key=lambda x: x["priority"])

    def _optimize_task(self, task: Dict[str, Any]) -> bool:
        """Execute a single optimization task.

        Args:
            task (Dict[str, Any]): Task configuration

        Returns:
            bool: True if task completed successfully, False otherwise
        """
        try:
            logging.info(f"_optimize_task: Starting task {task['name']}")
            result = task["function"]()
            logging.info(f"_optimize_task: Completed task {task['name']}")
            return result
        except Exception as e:
            logging.error(f"_optimize_task: Failed to execute task {task['name']}: {e}")
            return False

    def adjust_memory_usage(self) -> bool:
        """Adjust system memory usage based on available memory using centralized configuration.

        This function uses a centralized configuration approach to manage memory thresholds
        and corresponding system adjustments. The configuration includes:
        - Memory thresholds for different usage levels
        - Thread count adjustments for each level
        - Process priority adjustments
        - Cache clearing triggers

        Returns:
            bool: True if adjustment was successful, False otherwise.

        Raises:
            MemoryOptimizationError: If memory adjustment fails.
        """
        try:
            self.logger.info("Adjusting memory usage using centralized configuration")
            system_memory = psutil.virtual_memory()

            # Load memory management configuration
            memory_config = {
                "critical": {
                    "threshold": 2 * 1024**3,  # 2GB
                    "max_threads": 2,
                    "process_priority": psutil.HIGH_PRIORITY_CLASS,
                    "clear_cache": True,
                },
                "warning": {
                    "threshold": 4 * 1024**3,  # 4GB
                    "max_threads": 4,
                    "process_priority": psutil.ABOVE_NORMAL_PRIORITY_CLASS,
                    "clear_cache": True,
                },
                "normal": {
                    "threshold": 8 * 1024**3,  # 8GB
                    "max_threads": 8,
                    "process_priority": psutil.NORMAL_PRIORITY_CLASS,
                    "clear_cache": False,
                },
            }

            # Determine current memory state
            if system_memory.available < memory_config["critical"]["threshold"]:
                current_state = "critical"
            elif system_memory.available < memory_config["warning"]["threshold"]:
                current_state = "warning"
            else:
                current_state = "normal"

            # Apply memory optimizations
            state_config = memory_config[current_state]

            # Update thread configuration
            self.config.config.set(
                "Performance", "max_threads", str(state_config["max_threads"])
            )
            self.config.save_config()

            # Adjust process priority if on Windows
            if platform.system() == "Windows":
                current_process = psutil.Process()
                current_process.nice(state_config["process_priority"])

            # Clear system cache if needed
            if state_config["clear_cache"]:
                self._clear_system_cache()

            self.logger.info(
                f"Memory optimization applied - State: {current_state}, "
                f"Usage: {system_memory.percent}%, "
                f"Threads: {state_config['max_threads']}"
            )

            return True
        except Exception as e:
            error_msg = f"Failed to adjust memory usage: {str(e)}"
            self.logger.error(error_msg)
            raise MemoryOptimizationError(system_memory.percent, 75, {"error": str(e)})

    def _clear_system_cache(self) -> None:
        """Clear system cache to free up memory.

        This is a helper method for memory optimization that attempts to clear
        various system caches depending on the operating system.
        """
        try:
            if platform.system() == "Windows":
                # On Windows, we can suggest garbage collection
                import gc

                gc.collect()

                # Clear disk cache using built-in tools
                os.system('powershell -Command "Clear-DnsClientCache"')
                os.system('powershell -Command "Clear-BCCache -Force"')

            self.logger.info("System cache cleared successfully")
        except Exception as e:
            self.logger.warning(f"Failed to clear system cache: {e}")

    def get_log_path(self) -> Path:
        """Get the path for optimization logs.

        Returns:
            Path: Path to the log file
        """
        log_path = (
            self.config.output_dir / "optimization_logs" / f"{platform.node()}.log"
        )
        log_path.parent.mkdir(parents=True, exist_ok=True)
        return log_path

    def clean_temp_files(self) -> Dict[str, Any]:
        """Clean temporary files from system temporary directories using a targeted approach.

        The function uses the following strategies:
        1. Checks disk space and adjusts cleanup aggressiveness
        2. Targets specific file types based on age and size
        3. Preserves important system temp files
        4. Uses a gradual cleanup approach based on file age

        Returns:
            Dict[str, Any]: Cleanup operation results including success status,
                          files removed count and any errors encountered

        Raises:
            FileCleanupError: If cleanup process encounters critical errors or disk space check fails.
        """
