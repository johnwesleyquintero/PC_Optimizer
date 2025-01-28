# PC Optimizer

This project aims to provide a comprehensive solution for optimizing PC performance, managing configurations, and improving the overall user experience. It includes both a command-line interface (CLI) and a graphical user interface (GUI) for accessibility.

## Project Structure

The project is organized into several directories based on functionality:

- `src/`: Contains the source code for the application.
  - `cli/`: Contains modules for the command-line interface (CLI). `pc_optimizer_cli_v2.py` is the main CLI script.
  - `gui/`: Contains modules for the graphical user interface (GUI). `pc_optimizer_gui_v2.py` is the main GUI script.
  - `core/`: Core functionality used across the application. Includes modules for data analysis (`data_analyzer.py`), configuration management (`config_manager_v2.py`), environment management (`environment_manager.py`), and performance optimization (`performance_optimizer_v2.py`).
- `build/`: Stores build artifacts (auto-generated).
- `dist/`: Contains distribution outputs.
- `config/`: Holds configuration files (`config.ini`).
- `scripts/`: Includes build and deployment scripts (`build.bat`).
- `spec/`: Contains PyInstaller spec files for building executables (`PC_Optimizer_CLI_v2.spec`, `PC_Optimizer_GUI_v2.spec`, `PCOptimizerGUI.spec`, `sysopt.spec`).
- `docs/`: Documentation for the project.
- `venv/`: Virtual environment for managing project dependencies (should be added to `.gitignore`).

## Getting Started

1. Clone the repository:

   ```bash
   git clone <repository_url>
   cd PC_Optimizer
   ```

2. Create and activate a virtual environment (recommended):

   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### CLI

Run the command-line interface using:

```bash
python src/cli/pc_optimizer_cli_v2.py
```

### Data Analyzer Executable

To run the data analyzer as a standalone executable:

```bash
dist\data_analyzer.exe <csv_file_path>
```

Replace `<csv_file_path>` with the path to your CSV file. You can also use the `--help` flag to see available options:

```bash
dist\data_analyzer.exe --help
```

### GUI

Launch the graphical user interface with:

```bash
python src/gui/pc_optimizer_gui_v2.py
```

## Building Executables

Use the provided spec files and the `build.bat` script to create standalone executables:

```bash
# Install PyInstaller (if not already installed)
pip install pyinstaller

# Run the build script
.\scripts\build.bat
```

## Configuration

The application uses a configuration file located at `config/config.ini`. You can modify settings such as the optimization level in this file.

## CSV Data Analysis Features

The `src/core/data_analyzer.py` module provides functionalities for analyzing and transforming CSV data. See the module's docstrings for detailed information.

## Contributing

Contributions are welcome! Please follow the guidelines in a `CONTRIBUTING.md` file (to be created) when submitting pull requests or issues.

## License

This project is licensed under the MIT License - see the `LICENSE` file (to be created) for details.

## Troubleshooting

- **Error: ModuleNotFoundError:** Ensure all required packages are installed using `pip install -r requirements.txt`.
- **Error: File not found:** Verify file paths in your code and configuration files.
- **Other errors:** Check the console output for specific error messages and refer to the project documentation for solutions.

## Code Enhancements

### Improved Error Handling in `performance_optimizer_v2.py`

The `clean_temp_files` function in `src/core/performance_optimizer_v2.py` has been enhanced with more specific error handling. It now distinguishes between `OSError` exceptions, which are common during file system operations, and other unexpected exceptions. This allows for more targeted logging and debugging in case of issues during temporary file cleaning.

### Added Logging in `config_manager_v2.py`

Logging has been added to the `save_config` function in `src/core/config_manager_v2.py`. This provides better visibility into the configuration saving process, logging both successful saves and any exceptions that may occur. This is useful for debugging and ensuring that configuration changes are properly persisted.

## Future Enhancements

- [List potential future enhancements]
