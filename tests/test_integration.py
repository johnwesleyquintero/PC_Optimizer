import unittest
from unittest.mock import patch, MagicMock
from src.core.sentinel_core import SentinelCore
from src.core.monitoring_manager import MonitoringManager
from src.core.config_manager import ConfigManager
from src.gui.gui_worker import GUIWorker


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.mock_gui = MagicMock()
        self.gui_worker = GUIWorker(self.mock_gui)
        self.sentinel = SentinelCore()
        self.config = ConfigManager()

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    def test_full_optimization_flow(self, mock_mem, mock_cpu):
        # Initialize with test config
        test_config = {"metrics_history_size": 50}
        self.assertTrue(self.sentinel.initialize())

        # Run optimization
        result = self.sentinel.optimize_system("performance")
        self.assertTrue(result["success"])

        # Verify metrics collection
        metrics = self.sentinel.monitoring.get_system_metrics()
        self.assertIn("cpu_percent", metrics["current_metrics"])

        # Verify GUI updates
        self.mock_gui.update_metrics.assert_called()

    def test_component_initialization(self):
        self.assertTrue(self.sentinel.initialize())
        self.assertIsInstance(self.sentinel.monitoring, MonitoringManager)
        self.assertIsInstance(self.sentinel.config, ConfigManager)

    @patch.object(ConfigManager, "load_config", return_value=False)
    def test_config_failure_handling(self, mock_load):
        with self.assertRaises(RuntimeError):
            self.sentinel.initialize()

    def test_metrics_visualization(self):
        self.gui_worker.handle_metrics_update({"cpu_percent": 30})
        self.mock_gui.update_cpu_gauge.assert_called_with(30)

    @patch("subprocess.run")
    def test_build_process(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        result = self.gui_worker.run_build_process()
        self.assertTrue(result["success"])

    @patch.object(SentinelCore, "optimize_system")
    def test_worker_thread_exceptions(self, mock_optimize):
        mock_optimize.side_effect = Exception("Simulated failure")
        result = self.gui_worker.run_optimization()
        self.assertIn("Simulated failure", result["error"])

    def test_config_validation(self):
        invalid_config = {"metrics_history_size": -50}
        with self.assertRaises(ValueError):
            self.sentinel.update_config(invalid_config)

    @patch("psutil.sensors_temperatures")
    def test_benchmark_performance(self, mock_temp):
        mock_temp.return_value = {"coretemp": [MagicMock(current=65.0)]}
        report = self.sentinel.monitoring.get_performance_summary()
        self.assertLess(report["avg_cpu_usage"], 100)


if __name__ == "__main__":
    unittest.main()
