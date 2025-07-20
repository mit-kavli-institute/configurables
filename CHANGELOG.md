# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive type hints throughout the module
- NumPy-style docstrings for all classes and functions
- Sphinx documentation with Furo theme
- GitHub Actions workflow for documentation deployment
- Automatic versioning system using python-semantic-release
- Conventional commit message guidelines

### Changed
- Migrated version management to `_version.py`
- Updated documentation to dynamically import version
- Synchronized README between root and documentation

### Fixed
- Fixed mypy type checking errors
- Resolved flake8 linting issues

## [1.1.0] - Previous Release

### Added
- Initial stable release with core functionality
- Support for INI configuration files
- Environment variable resolution
- Command-line argument parsing
- Configurable resolution order
- Parameter and option decorators

## [0.1.0] - 2022-05-12

### Added
- First release on PyPI
- Basic configuration management functionality

[Unreleased]: https://github.com/mit-kavli-institute/configurables/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/mit-kavli-institute/configurables/compare/v0.1.0...v1.1.0
[0.1.0]: https://github.com/mit-kavli-institute/configurables/releases/tag/v0.1.0