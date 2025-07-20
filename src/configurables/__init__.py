"""
Configurables - A decorator-based configuration management system.

Configurables provides a simple yet powerful way to manage configuration from
multiple sources (files, environment variables, command-line arguments) for
Python applications. It uses decorators to define configuration schemas and
automatically handles type conversion and validation.

Key Features
------------
- Decorator-based configuration schema definition
- Multiple configuration sources with customizable precedence
- Automatic type conversion and validation
- Configuration file generation
- Support for required parameters and optional parameters with defaults

Quick Start
-----------
>>> from configurables import configurable, param, option
>>> 
>>> @configurable("Database")
... @param("host", type=str)
... @param("port", type=int)
... @option("timeout", type=int, default=30)
... def connect(host, port, timeout):
...     return f"Connecting to {host}:{port} (timeout={timeout}s)"
>>> 
>>> # Use with configuration file
>>> result = connect("config.ini")
>>> 
>>> # Generate template configuration
>>> connect.emit("template.ini")

Configuration Sources
--------------------
By default, configuration is resolved in this order (highest to lowest precedence):
1. Command-line arguments (--key value)
2. Configuration files (.ini, .conf)
3. Environment variables

This order can be customized using the resolution operators:
>>> from configurables import ENV, CFG, CLI
>>> @configurable("MyApp", order=ENV > CFG > CLI)
... def my_function(...):
...     pass
"""
from configurables.configurable import configurable, configure, option, param
from configurables.parse import CFG, CLI, ENV
from configurables._version import __version__

__author__ = """William Christopher Fong"""
__email__ = "willfong@mit.edu"


__all__ = [
    "configure",
    "param",
    "option",
    "configurable",
    "ENV",
    "CFG",
    "CLI",
]
