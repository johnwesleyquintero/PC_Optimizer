import logging
from pathlib import Path
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import psutil
import platform
import os
import shutil
from .environment_manager import EnvironmentConfig

# Configure logging
logging.basicConfig(
    filename='pc_optimizer.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class OptimizationError(Exception):
    """Custom exception for optimization-related errors."""
    pass

class PerformanceOptimizer:
    def __init__(self):
        self.config = EnvironmentConfig()

    def optimize_system(self) -> bool:
        """Optimize system performance using multiple optimization strategies.

        Returns:
            bool: True if optimization was successful, False otherwise.
        """
        try:
            logging.info("optimize_system: Starting system optimization")
            
            # Adjust system based on theme
            if self.config.theme == 'dark':
                self._apply_dark_mode_performance()
            
            # Get optimization tasks
            tasks = self._get_tasks()
            if not tasks:
                logging.warning("No optimization tasks found")
                return True

            # Execute tasks using thread pool
            thread_count = min(self.config.max_threads, len(tasks))
            with ThreadPoolExecutor(max_workers=thread_count) as executor:
                results = list(executor.map(self._optimize_task, tasks))
            
            # Check results
            if not all(results):
                logging.warning("Some optimization tasks failed")
                return False
                
            logging.info("optimize_system: System optimization completed successfully")
            return True
            
        except Exception as e:
            logging.error(f"optimize_system: Failed to optimize system: {e}")
            raise OptimizationError(f"Failed to optimize system: {e}")

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
        """
        try:
            logging.info("adjust_memory_usage: Adjusting memory usage")
            system_memory = psutil.virtual_memory().available
            
            if system_memory < 2 * 1024**3:  # Less than 2GB available
                self.config.config.set('Performance', 'max_threads', '2')
                self.config.save_config()
                logging.info("Memory usage adjusted: reduced max threads to 2")
            else:
                logging.info("Memory usage is within acceptable range")
            
            return True
        except Exception as e:
            logging.error(f"adjust_memory_usage: Failed to adjust memory usage: {e}")
            return False

    def get_log_path(self) -> Path:
        """Get the path for optimization logs.

        Returns:
            Path: Path to the log file
        """
        log_path = self.config.output_dir / 'optimization_logs' / f'{platform.node()}.log'
        log_path.parent.mkdir(parents=True, exist_ok=True)
        return log_path

    def clean_temp_files(self):
        logging.info("clean_temp_files: Cleaning temporary files")
        temp_dir = os.environ.get("TEMP") or os.environ.get("TMP")
        if not temp_dir:
            temp_dir = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Temp")

        logging.info(f"Cleaning temporary files from: {temp_dir}")
        cleaned_files_count = 0
        errors = []
        if os.path.isdir(temp_dir):
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                        cleaned_files_count += 1
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                        cleaned_files_count += 1
                except OSError as e:
                    errors.append(f"Error deleting {file_path}: {e}")
                    logging.error(f"OSError deleting {file_path}: {e}")
                except Exception as e:
                    errors.append(f"Unexpected error deleting {file_path}: {e}")
                    logging.exception(f"Unexpected error deleting {file_path}: {e}")

        if errors:
            logging.warning(f"Errors occurred during temporary file cleaning: {errors}")
            return False
        else:
            logging.info(f"Successfully cleaned {cleaned_files_count} temporary files.")
            logging.info("clean_temp_files: Temporary files cleaning completed")
            return True
