import platform
import os
import sys
import configparser

class EnvironmentConfig:
    """
    Manages environment-specific configurations for the PC Optimizer application.

    This class detects the operating system, determines the appropriate theme,
    sets the maximum number of threads to be used, and specifies the output directory
    for reports and logs.
    """

    def __init__(self, config_file='config/config.ini'):
        """
        Initializes the EnvironmentConfig with default or configuration file settings.

        Args:
            config_file (str): Path to the configuration file.
        """
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        self.system = self._detect_os()
        self.theme = self._get_theme()
        self.max_threads = self._get_max_threads()
        self.output_dir = self._get_output_dir()

    def _detect_os(self):
        """
        Detects the operating system.

        Returns:
            str: The name of the operating system.
        """
        return platform.system()

    def _get_theme(self):
        """
        Determines the application theme based on the OS or configuration file.

        Returns:
            str: The selected theme ('dark' or 'light').
        """
        if self.system == 'Windows':
            # Example: Use dark theme on Windows
            return self.config.get('Theme', 'WindowsTheme', fallback='dark')
        elif self.system == 'Darwin':
            # Example: Use light theme on macOS
            return self.config.get('Theme', 'MacTheme', fallback='light')
        else:
            # Default theme
            return self.config.get('Theme', 'DefaultTheme', fallback='light')

    def _get_max_threads(self):
        """
        Determines the maximum number of threads to be used, based on the OS or configuration file.

        Returns:
            int: The maximum number of threads.
        """
        if self.system == 'Windows':
            # Example: Use 4 threads on Windows
            return self.config.getint('Threads', 'WindowsThreads', fallback=4)
        elif self.system == 'Darwin':
            # Example: Use 2 threads on macOS
            return self.config.getint('Threads', 'MacThreads', fallback=2)
        else:
            # Default number of threads
            return self.config.getint('Threads', 'DefaultThreads', fallback=os.cpu_count() or 1)

    def _get_output_dir(self):
        """
        Specifies the output directory for reports and logs, based on the OS or configuration file.

        Returns:
            str: The path to the output directory.
        """
        if self.system == 'Windows':
            # Example: Use a specific directory on Windows
            output_dir = self.config.get('Output', 'WindowsOutputDir', fallback='C:/Users/MAG/Desktop/PC_Optimizer/reports')
        elif self.system == 'Darwin':
            # Example: Use a specific directory on macOS
            output_dir = self.config.get('Output', 'MacOutputDir', fallback=os.path.expanduser('~/Documents/PC_Optimizer/reports'))
        else:
            # Default output directory
            output_dir = self.config.get('Output', 'DefaultOutputDir', fallback=os.path.join(os.getcwd(), 'reports'))

        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
