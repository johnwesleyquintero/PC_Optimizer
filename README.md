<p align="center">
  <img src="_wwwroot/Assets/Branding/logo.svg" alt="Sentinel PC Logo" width="400">
</p>

<h1 align="center">Your Ultimate Workspace Guardian 🛡️</h1>

> This project aims to provide a comprehensive solution for optimizing PC performance, managing configurations, and improving the overall user experience. It features a unified interface with both CLI and GUI capabilities, internationalization support, and advanced monitoring systems.

[![Netlify Status](https://api.netlify.com/api/v1/badges/dee96004-2646-4fee-881e-015bdd75685d/deploy-status)](https://app.netlify.com/sites/wq-resume/deploys)

## Project Structure

The project is organized into several directories based on functionality:

- `src/`: Contains the source code for the application.
  - `cli/`: Command-line interface modules (`sentinel_cli.py`, `build_cli.py`).
  - `gui/`: Graphical user interface modules (`sentinel_gui.py`).
  - `core/`: Core functionality including:
    - Data analysis (`data_analyzer.py`)
    - Configuration management (`config_manager.py`)
    - Environment management (`environment_manager.py`)
    - Performance optimization (`performance_optimizer.py`)
    - Internationalization (`i18n_manager.py`)
    - Accessibility features (`accessibility_manager.py`)
    - Monitoring systems (`monitoring_manager.py`)
    - Feature flags (`feature_flags.py`)
    - Service layer (`service_layer.py`)
- `build/`: Stores build artifacts (auto-generated)
- `dist/`: Contains distribution outputs
- `config/`: Configuration files (`config.ini`)
- `scripts/`: Build and deployment scripts
- `spec/`: PyInstaller spec files
- `docs/`: Project documentation
- `locales/`: Internationalization files
- `_wwwroot/`: Web assets and resources
- `tests/`: Unit and integration tests

## Getting Started

1. Clone the repository:

   ```bash
   git clone <repository_url>
   cd SentinelPC
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
4. Run the application:
   ```bash
   python src/sentinel_gui.py
   ```
## CLI Usage
To use the command-line interface (CLI), run the following command:
```bash
python src/sentinel_cli.py
```
The CLI will guide you through various configuration options and provide real-time performance metrics.
## GUI Usage
To use the graphical user interface (GUI), run the following command:
```bash
python src/sentinel_gui.py
```
The GUI will provide a user-friendly interface for configuring and monitoring your PC.

## Building the Application
To build the application, use the provided build scripts:
```bash
# Build for Windows
python scripts/build_unified.py
```
## Workarounds

```bash
.\build.bat
```

## Usage 

### Unified Interface   

Run the SentinelPC application:

```bash
dist\SentinelPC.exe
```

The application will automatically detect your preferences and launch in either CLI or GUI mode. You can force a specific mode using command-line arguments:

```bash
dist\SentinelPC.exe --cli  # Force CLI mode
dist\SentinelPC.exe --gui  # Force GUI mode
```

## Building the Application

Use the unified build script to create the executable:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run the unified build script
python scripts/build_unified.py
```

## Configuration

The application uses a configuration file located at `config/config.ini`. You can modify settings such as:
- Optimization level
- Language preferences
- Feature flags
- Monitoring options
- Accessibility settings

## Features

### Internationalization
The application supports multiple languages through the `i18n_manager.py` module. Language files are stored in the `locales/` directory.

### Accessibility
Built-in accessibility features are managed by `accessibility_manager.py`, ensuring the application is usable by everyone.

### Monitoring System
The `monitoring_manager.py` provides real-time system monitoring and performance metrics.

### Feature Flags
Feature flags in `feature_flags.py` allow for gradual rollout of new features and A/B testing.

## Contributing

Contributions are welcome! Please read `CONTRIBUTING.md` for guidelines on how to submit pull requests and report issues.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## Troubleshooting

- **Error: ModuleNotFoundError:** Ensure all required packages are installed using `pip install -r requirements.txt`
- **Error: File not found:** Verify file paths in your code and configuration files
- **Other errors:** Check the console output and logs in `SentinelPC.log`

## Future Enhancements

- Enhanced monitoring capabilities with machine learning integration
- Extended accessibility features
- Additional language support
- Cloud synchronization capabilities
- Advanced performance optimization algorithms
