from pathlib import Path
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import psutil
import platform
import os
import shutil
from .environment_manager import EnvironmentConfig
from .logging_manager import LoggingManager

class OptimizationError(Exception):
    """Custom exception for optimization-related errors."""
    pass

class TaskExecutionError(OptimizationError):
    """Exception raised when a specific optimization task fails."""
    pass

class MemoryOptimizationError(OptimizationError):
    """Exception raised when memory optimization fails."""
    pass

class FileCleanupError(OptimizationError):
    """Exception raised when temporary file cleanup fails."""
    pass

class PerformanceOptimizer:
    def __init__(self):
        self.config = EnvironmentConfig()
        self.logger = LoggingManager().get_logger(__name__)

    def optimize_system(self) -> bool:
        """Optimize system performance using multiple optimization strategies.

        Returns:
            bool: True if optimization was successful, False otherwise.

        Raises:
            OptimizationError: If optimization process fails.
            TaskExecutionError: If specific tasks fail during execution.
        """
        try:
            self.logger.info("Starting system optimization")
            
            # Adjust system based on theme
            if self.config.theme == 'dark':
                self._apply_dark_mode_performance()
            
            # Get optimization tasks
            tasks = self._get_tasks()
            if not tasks:
                self.logger.warning("No optimization tasks found")
                return True

            # Execute tasks using thread pool
            thread_count = min(self.config.max_threads or multiprocessing.cpu_count(), len(tasks))
            failed_tasks = []
            
            with ThreadPoolExecutor(max_workers=thread_count) as executor:
                future_to_task = {executor.submit(self._optimize_task, task): task for task in tasks}
                for future in future_to_task:
                    task = future_to_task[future]
                    try:
                        if not future.result():
                            failed_tasks.append(task['name'])
                    except Exception as e:
                        self.logger.error(f"Task {task['name']} failed with error: {str(e)}")
                        failed_tasks.append(task['name'])
            
            if failed_tasks:
                error_msg = f"Failed tasks: {', '.join(failed_tasks)}"
                self.logger.error(error_msg)
                raise TaskExecutionError(error_msg)
                
            self.logger.info("System optimization completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to optimize system: {str(e)}")
            raise OptimizationError(f"Failed to optimize system: {str(e)}")

    def _apply_dark_mode_performance(self):
        # Windows-specific dark mode optimizations
        if self.config.system == 'Windows':
            self._adjust_windows_theme_performance()

    def _adjust_windows_theme_performance(self):
        # Placeholder for Windows theme perf. adjustments
        pass


    def _get_tasks(self) -> List[Dict[str, Any]]:
        """Get list of optimization tasks to perform.

        Returns:
            List[Dict[str, Any]]: List of task configurations
        """
        tasks = [
            {
                'name': 'memory_optimization',
                'function': self.adjust_memory_usage,
                'priority': 1
            },
            {
                'name': 'temp_cleanup',
                'function': self.clean_temp_files,
                'priority': 2
            }
        ]
        return sorted(tasks, key=lambda x: x['priority'])

    def _optimize_task(self, task: Dict[str, Any]) -> bool:
        """Execute a single optimization task.

        Args:
            task (Dict[str, Any]): Task configuration

        Returns:
            bool: True if task completed successfully, False otherwise
        """
        try:
            logging.info(f"_optimize_task: Starting task {task['name']}")
            result = task['function']()
            logging.info(f"_optimize_task: Completed task {task['name']}")
            return result
        except Exception as e:
            logging.error(f"_optimize_task: Failed to execute task {task['name']}: {e}")
            return False

    def adjust_memory_usage(self) -> bool:
        """Adjust system memory usage based on available memory.

        Returns:
            bool: True if adjustment was successful, False otherwise.

        Raises:
            MemoryOptimizationError: If memory adjustment fails.
        """
        try:
            self.logger.info("Adjusting memory usage")
            system_memory = psutil.virtual_memory()
            
            # Calculate memory thresholds
            critical_threshold = 2 * 1024**3  # 2GB
            warning_threshold = 4 * 1024**3   # 4GB
            
            if system_memory.available < critical_threshold:
                self.config.config.set('Performance', 'max_threads', '2')
                self.config.save_config()
                self.logger.warning(f"Critical memory condition: {system_memory.percent}% used. Reduced max threads to 2")
            elif system_memory.available < warning_threshold:
                self.config.config.set('Performance', 'max_threads', '4')
                self.config.save_config()
                self.logger.info(f"Low memory condition: {system_memory.percent}% used. Adjusted max threads to 4")
            else:
                self.logger.info(f"Memory usage is optimal: {system_memory.percent}% used")
            
            return True
        except Exception as e:
            error_msg = f"Failed to adjust memory usage: {str(e)}"
            self.logger.error(error_msg)
            raise MemoryOptimizationError(error_msg)

    def get_log_path(self) -> Path:
        """Get the path for optimization logs.

        Returns:
            Path: Path to the log file
        """
        log_path = self.config.output_dir / 'optimization_logs' / f'{platform.node()}.log'
        log_path.parent.mkdir(parents=True, exist_ok=True)
        return log_path

    def clean_temp_files(self) -> bool:
        """Clean temporary files from system temporary directories.

        Returns:
            bool: True if cleanup was successful, False otherwise.

        Raises:
            FileCleanupError: If cleanup process encounters critical errors.
        """
        self.logger.info("Starting temporary files cleanup")
        temp_dirs = []

        # Get all possible temp directories
        for env_var in ["TEMP", "TMP"]:
            if path := os.environ.get(env_var):
                temp_dirs.append(Path(path))
        
        if not temp_dirs:
            temp_dirs.append(Path(os.environ["USERPROFILE"]) / "AppData" / "Local" / "Temp")

        cleaned_files_count = 0
        errors = []

        for temp_dir in temp_dirs:
            if not temp_dir.is_dir():
                continue

            self.logger.info(f"Cleaning temporary files from: {temp_dir}")
            try:
                for item in temp_dir.iterdir():
                    try:
                        if item.is_file() or item.is_symlink():
                            item.unlink(missing_ok=True)
                            cleaned_files_count += 1
                        elif item.is_dir():
                            shutil.rmtree(item, ignore_errors=True)
                            cleaned_files_count += 1
                    except PermissionError as e:
                        self.logger.debug(f"Permission denied for {item}: {str(e)}")
                    except OSError as e:
                        errors.append(f"Error processing {item}: {str(e)}")
                        self.logger.warning(f"Failed to remove {item}: {str(e)}")
            except Exception as e:
                error_msg = f"Critical error while cleaning {temp_dir}: {str(e)}"
                self.logger.error(error_msg)
                raise FileCleanupError(error_msg)

        if errors:
            self.logger.warning(f"Completed with {len(errors)} non-critical errors")
            return False

        self.logger.info(f"Successfully cleaned {cleaned_files_count} temporary items")
        return True
