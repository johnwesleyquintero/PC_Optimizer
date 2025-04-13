import unittest
from src.core.config_manager import EnvironmentConfig

class TestEnvironmentConfig(unittest.TestCase):
    def setUp(self):
        self.config = EnvironmentConfig()

    def test_load_config(self):
        # Basic test to check if config loads without errors
        try:
            self.config._load_config()
        except Exception as e:
            self.fail(f"_load_config raised an exception: {e}")

if __name__ == '__main__':
    unittest.main()