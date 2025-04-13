# Contributing to SENTINEL PC Optimizer

Thank you for your interest in contributing to SENTINEL PC Optimizer! This document provides guidelines and instructions for contributing to the project.

## Development Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # Unix/MacOS
   ```

2. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

## Code Style

- Follow PEP 8 style guide for Python code
- Use `black` for code formatting
- Use `flake8` for linting
- Add docstrings for all public functions and classes
- Keep functions focused and concise

## Testing

- Write unit tests for new features using `pytest`
- Ensure all tests pass before submitting a PR
- Maintain or improve code coverage

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to your fork (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Commit Guidelines

- Use clear and descriptive commit messages
- Reference issues and pull requests in commit messages
- Keep commits focused and atomic

## Code Review

- All submissions require review
- Address review feedback promptly
- Be respectful and constructive in discussions

## Reporting Issues

- Use the GitHub issue tracker
- Include clear steps to reproduce bugs
- Provide system information when relevant
- Check existing issues before creating new ones

## License

By contributing, you agree that your contributions will be licensed under the MIT License.