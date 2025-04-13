import unittest
from src.core.performance_optimizer import PerformanceOptimizer

class TestPerformanceOptimizer(unittest.TestCase):
    def setUp(self):
        self.optimizer = PerformanceOptimizer()

    def test_optimize_system(self):
        # Basic test to check if optimize_system runs without errors
        try:
            self.optimizer.optimize_system()
        except Exception as e:
            self.fail(f"optimize_system raised an exception: {e}")

if __name__ == '__main__':
    unittest.main()