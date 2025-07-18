# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Configurables is a Python package that provides a decorator-based system for managing configuration from multiple sources (configuration files, environment variables, and command-line arguments). It's designed for scientific computing pipelines where parameters need to be loaded from various sources with proper type conversion and validation.

## Development Commands

### Essential Commands
- **Run tests**: `make test` or `pytest`
- **Run all tests (multiple Python versions)**: `make test-all` or `tox`
- **Run specific test**: `pytest tests/test_specific.py::test_name`
- **Lint code**: `make lint` (runs flake8 and black)
- **Format code**: `black src tests --line-length 79`
- **Type check**: `mypy src/configurables`
- **Coverage**: `make coverage`
- **Build docs**: `make docs`
- **Build package**: `make dist`
- **Clean artifacts**: `make clean`

### Testing Strategy
- Tests use pytest with hypothesis for property-based testing
- Test files are in `tests/` directory
- Use `conftest.py` for shared fixtures
- Coverage should be maintained above current levels

## Architecture Overview

The package follows a clean architecture with these core modules:

### Core Modules
1. **`core.py`**: Contains fundamental classes
   - `Parameter`: Required configuration parameter
   - `Option`: Optional parameter with default
   - `ConfigurationBuilder`: Accumulates function schema
   - `ConfigurationFactory`: Main class that resolves and applies configuration

2. **`configurable.py`**: Decorator API
   - `@configurable`: Main decorator to make functions configurable
   - `@param`: Define required parameters
   - `@option`: Define optional parameters with defaults
   - `configure()`: Simple configuration without schema

3. **`parse.py`**: Configuration resolution
   - `ResolutionDefinition`: Manages source precedence (default: CLI > CFG > ENV)
   - `Interpreter` classes: Handle different configuration sources
   - Registry pattern for file format parsers

4. **`emission.py`**: Configuration file generation
   - `autoemit_config()`: Writes configuration templates
   - Registry for output formats (.ini, .conf)

### Key Design Patterns
- **Builder Pattern**: Building configuration schema with decorators
- **Factory Pattern**: Creating configured functions
- **Registry Pattern**: Extensible file format support
- **Chain of Responsibility**: Configuration source precedence

### Configuration Flow
```
Function Definition → Decorators → ConfigurationFactory → Resolution → Execution
                         ↓                                     ↓
                  Schema Building                    CLI > CFG > ENV
```

## Development Guidelines

### Adding New Features
- New file format parsers go in `parse.py` and register with `register_parser`
- New emitters go in `emission.py` and register with `register_emitter`
- Maintain backwards compatibility - this is a public API

### Code Style
- Black formatting with 79-character line length
- Type hints are encouraged
- Follow existing patterns in the codebase

### Testing Requirements
- Write tests for new functionality
- Use hypothesis for property-based testing where appropriate
- Ensure all tests pass with `tox` before submitting changes

## Python Version Support
- Supports Python 3.9, 3.10, 3.11, 3.12
- CI tests against all supported versions
- Use `tox` to test locally against multiple versions