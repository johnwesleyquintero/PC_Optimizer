# SentinelPC CLI User Guide

## Introduction

This guide provides basic instructions on how to use the SentinelPC command-line interface (CLI).

## Getting Started

1.  Open your terminal or command prompt.
2.  Navigate to the directory where the `sentinel_cli.py` file is located.
3.  Run the script using the following command:

    ```bash
    python src/cli/sentinel_cli.py [options]
    ```

## Available Options

*   `--help`: Displays help message with available commands and options.

## Examples

### Display Help Message

```bash
python src/cli/sentinel_cli.py --help
```

### Run System Optimization

```bash
python src/cli/sentinel_cli.py optimize
```

### Get System Information

```bash
python src/cli/sentinel_cli.py info
```

## Configuration

The CLI uses the same configuration file as the GUI, located at `config/config.ini`. You can modify this file to adjust various settings.

## Troubleshooting

If you encounter any issues, please consult the application logs or refer to the documentation for more information.