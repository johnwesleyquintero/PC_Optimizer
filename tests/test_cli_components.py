import unittest
from unittest.mock import patch, MagicMock
from src.cli.sentinel_cli import SentinelCLI
from src.core.cli_manager import CLIManager

class TestCLIComponents(unittest.TestCase):
    def setUp(self):
        self.cli = SentinelCLI()
        self.cli_manager = CLIManager()

    @patch('argparse.ArgumentParser.parse_args')
    def test_cli_argument_parsing(self, mock_args):
        """Test CLI argument parsing functionality."""
        mock_args.return_value = MagicMock(
            action='optimize',
            mode='performance',
            verbose=True
        )
        args = self.cli.parse_arguments()
        self.assertEqual(args.action, 'optimize')
        self.assertEqual(args.mode, 'performance')
        self.assertTrue(args.verbose)

    @patch('src.core.cli_manager.CLIManager.execute_command')
    def test_command_execution(self, mock_execute):
        """Test command execution through CLI manager."""
        mock_execute.return_value = {'success': True, 'message': 'Command executed'}
        result = self.cli_manager.execute_command('optimize', {'mode': 'performance'})
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], 'Command executed')

    @patch('sys.stdout')
    def test_output_formatting(self, mock_stdout):
        """Test CLI output formatting."""
        test_metrics = {'cpu_percent': 50, 'memory_used': 4000}
        self.cli.display_metrics(test_metrics)
        mock_stdout.write.assert_called()

    def test_error_handling(self):
        """Test CLI error handling."""
        with self.assertRaises(ValueError):
            self.cli_manager.execute_command('invalid_command', {})

    @patch('src.core.cli_manager.CLIManager.get_system_status')
    def test_status_command(self, mock_status):
        """Test system status retrieval through CLI."""
        mock_status.return_value = {
            'status': 'healthy',
            'metrics': {'cpu_percent': 30}
        }
        result = self.cli_manager.get_system_status()
        self.assertEqual(result['status'], 'healthy')
        self.assertIn('metrics', result)

    def test_help_command(self):
        """Test help command output."""
        with patch('sys.stdout') as mock_stdout:
            self.cli.show_help()
            mock_stdout.write.assert_called()

if __name__ == '__main__':
    unittest.main()