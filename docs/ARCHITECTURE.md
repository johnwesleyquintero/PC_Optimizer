# SentinelPC Architecture

## Overview
SentinelPC is a unified PC optimization application that provides both CLI and GUI interfaces while sharing a common core functionality. This document outlines the architectural design and component integration.

## Component Structure

### 1. Core Layer (`src/core/`)
The foundation of SentinelPC containing all business logic and shared functionality.

#### Key Components:
- `sentinel_core.py`: Central core module managing all optimization operations
- `config_manager.py`: Configuration management
- `performance_optimizer.py`: System optimization logic
- `environment_manager.py`: System environment handling
- `logging_manager.py`: Centralized logging system

### 2. Interface Layer

#### CLI Interface (`src/cli/`)
- `sentinel_cli.py`: Command-line interface entry point
- Handles command parsing and CLI-specific logic
- Directly interfaces with Core Layer

#### GUI Interface (`src/gui/`)
- `sentinel_gui.py`: Graphical interface entry point
- Manages GUI components and event handling
- Interfaces with Core Layer through dedicated GUI controllers

### 3. Entry Points

#### Main Entry (`src/main.py`)
- Single entry point for both CLI and GUI modes
- Mode selection based on command-line arguments
- Initializes appropriate interface (CLI/GUI)

## Component Integration

### Data Flow
1. User Input → Interface Layer (CLI/GUI)
2. Interface Layer → Core Layer
3. Core Layer → System Operations
4. Results → Interface Layer → User

### Configuration Management
- Centralized configuration through `config_manager.py`
- Shared settings between CLI and GUI modes
- Environment-specific configurations

### Logging and Error Handling
- Unified logging through `logging_manager.py`
- Consistent error handling across all layers
- Different log levels for CLI and GUI modes

## Build Process

### Single Application Build
- PyInstaller spec file: `SentinelPC.spec`
- Builds single executable with both CLI and GUI capabilities
- Mode selection at runtime

## Version Management

### Semantic Versioning
- Format: MAJOR.MINOR.PATCH (e.g., v1.0.0)
- MAJOR: Incompatible API changes
- MINOR: Backwards-compatible features
- PATCH: Backwards-compatible fixes

## Future Considerations

### Extensibility
- Plugin architecture for additional optimizations
- Custom optimization profiles
- Remote management capabilities

### Testing Strategy
- Unit tests for Core Layer components
- Integration tests for Interface Layer
- End-to-end testing for complete workflows