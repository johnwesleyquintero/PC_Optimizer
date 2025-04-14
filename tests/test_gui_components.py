import unittest
from unittest.mock import MagicMock, patch
from src.gui.sentinel_gui import SentinelGUI
from src.gui.scrollable_frame import ScrollableFrame
from tkinter import Tk


class TestGUIComponents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Tk()
        cls.root.withdraw()  # Hide the window during tests

    def setUp(self):
        self.gui = SentinelGUI()
        self.gui.withdraw()  # Hide GUI window during tests

    def tearDown(self):
        if hasattr(self, "gui"):
            self.gui.destroy()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_scrollable_frame_creation(self):
        """Test ScrollableFrame widget initialization and basic properties."""
        frame = ScrollableFrame(self.root)
        self.assertIsNotNone(frame.canvas)
        self.assertIsNotNone(frame.scrollbar)
        self.assertIsNotNone(frame.scrollable_frame)

    @patch("tkinter.messagebox.showinfo")
    def test_about_dialog(self, mock_showinfo):
        """Test about dialog display."""
        self.gui.show_about()
        mock_showinfo.assert_called_once()

    @patch("src.gui.sentinel_gui.SentinelGUI.update_metrics")
    def test_metrics_update(self, mock_update):
        """Test metrics update handling."""
        test_metrics = {"cpu_percent": 50, "memory_percent": 60}
        self.gui.handle_metrics_update(test_metrics)
        mock_update.assert_called_with(test_metrics)

    def test_theme_switching(self):
        """Test theme switching functionality."""
        original_bg = self.gui.cget("bg")
        self.gui.toggle_theme()
        new_bg = self.gui.cget("bg")
        self.assertNotEqual(original_bg, new_bg)

    @patch("src.gui.sentinel_gui.SentinelGUI.start_optimization")
    def test_optimization_button(self, mock_start):
        """Test optimization button functionality."""
        self.gui.optimization_button.invoke()
        mock_start.assert_called_once()

    def test_error_handling(self):
        """Test error handling in GUI."""
        with self.assertRaises(Exception):
            self.gui.handle_error("Test error")


if __name__ == "__main__":
    unittest.main()
