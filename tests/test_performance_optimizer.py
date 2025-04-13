import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import psutil
import os
from src.core.performance_optimizer import (
    PerformanceOptimizer,
    OptimizationError,
    TaskExecutionError,
    MemoryOptimizationError,
    FileCleanupError
)

class TestPerformanceOptimizer(unittest.TestCase):
    def setUp(self):
        self.optimizer = PerformanceOptimizer()

    @patch('src.core.performance_optimizer.ThreadPoolExecutor')
    def test_optimize_system_success(self, mock_executor):
        # Mock successful task execution
        mock_context = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_context
        mock_future = MagicMock()
        mock_future.result.return_value = True
        mock_context.submit.return_value = mock_future

        result = self.optimizer.optimize_system()
        self.assertTrue(result)

    @patch('src.core.performance_optimizer.ThreadPoolExecutor')
    def test_optimize_system_task_failure(self, mock_executor):
        # Mock failed task execution
        mock_context = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_context
        mock_future = MagicMock()
        mock_future.result.return_value = False
        mock_context.submit.return_value = mock_future

        with self.assertRaises(TaskExecutionError):
            self.optimizer.optimize_system()

    @patch('psutil.virtual_memory')
    def test_adjust_memory_usage_critical(self, mock_vmem):
        # Mock critical memory condition
        mock_vmem.return_value = MagicMock(
            available=1 * 1024**3,  # 1GB available
            percent=90
        )

        self.optimizer.adjust_memory_usage()
        self.assertEqual(
            self.optimizer.config.config.get('Performance', 'max_threads'),
            '2'
        )

    @patch('psutil.virtual_memory')
    def test_adjust_memory_usage_warning(self, mock_vmem):
        # Mock warning memory condition
        mock_vmem.return_value = MagicMock(
            available=3 * 1024**3,  # 3GB available
            percent=70
        )

        self.optimizer.adjust_memory_usage()
        self.assertEqual(
            self.optimizer.config.config.get('Performance', 'max_threads'),
            '4'
        )

    @patch('psutil.virtual_memory')
    def test_adjust_memory_usage_optimal(self, mock_vmem):
        # Mock optimal memory condition
        mock_vmem.return_value = MagicMock(
            available=8 * 1024**3,  # 8GB available
            percent=30
        )

        result = self.optimizer.adjust_memory_usage()
        self.assertTrue(result)

    @patch('pathlib.Path.iterdir')
    @patch('pathlib.Path.is_file')
    @patch('pathlib.Path.unlink')
    def test_clean_temp_files_success(self, mock_unlink, mock_is_file, mock_iterdir):
        # Mock successful file cleanup
        mock_file = MagicMock()
        mock_file.is_file.return_value = True
        mock_file.is_symlink.return_value = False
        mock_iterdir.return_value = [mock_file]
        mock_is_file.return_value = True

        result = self.optimizer.clean_temp_files()
        self.assertTrue(result)
        mock_unlink.assert_called_once()

    @patch('pathlib.Path.iterdir')
    def test_clean_temp_files_permission_error(self, mock_iterdir):
        # Mock permission error during cleanup
        mock_file = MagicMock()
        mock_file.is_file.return_value = True
        mock_file.unlink.side_effect = PermissionError()
        mock_iterdir.return_value = [mock_file]

        result = self.optimizer.clean_temp_files()
        self.assertFalse(result)

    def test_get_log_path(self):
        log_path = self.optimizer.get_log_path()
        self.assertIsInstance(log_path, Path)
        self.assertTrue(str(log_path).endswith('.log'))

if __name__ == '__main__':
    unittest.main()