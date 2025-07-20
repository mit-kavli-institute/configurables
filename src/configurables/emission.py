"""
Configuration file emission module.

This module provides functionality for generating configuration file templates
from function schemas. It includes a registry system for different output
formats and built-in support for INI/CONF file generation.

The emission system allows configured functions to generate template
configuration files with their parameters and default values, making it
easy for users to create properly formatted configuration files.

Functions
---------
autoemit_config
    Automatically emit configuration based on file extension.
register
    Decorator to register emission handlers for file formats.
emit_init
    Emit configuration in INI/CONF format.

Examples
--------
>>> # Generate a template configuration file
>>> @configurable("Database")
... @param("host", type=str)
... @option("port", type=int, default=5432)
... def connect(host, port):
...     return f"Connecting to {host}:{port}"
>>> # Emit template
>>> connect.emit("db_template.ini")
"""
from __future__ import annotations

import configparser
import pathlib
import typing

# Registry mapping file extensions to emission functions
# Format: {'.ext': emit_function}
# Each function should have signature: (path, section, config) -> path
EMISSION_REGISTRY: dict[
    str,
    typing.Callable[
        [pathlib.Path, str, dict[typing.Any, typing.Any]], pathlib.Path
    ],
] = {}


def autoemit_config(
    path: pathlib.Path,
    configuration: dict[typing.Any, typing.Any],
    section: typing.Optional[str] = None,
) -> pathlib.Path:
    """
    Automatically emit configuration file based on path extension.
    
    This function looks up the appropriate emitter in the EMISSION_REGISTRY
    based on the file extension and uses it to write the configuration.
    
    Parameters
    ----------
    path : pathlib.Path
        Output path for the configuration file. The file extension
        determines which emitter to use.
    configuration : dict
        Configuration key-value pairs to write.
    section : str, optional
        Section name to use in the configuration file. Defaults to "DEFAULT".
        
    Returns
    -------
    pathlib.Path
        Absolute path to the written configuration file.
        
    Raises
    ------
    KeyError
        If no emitter is registered for the file extension.
        
    Examples
    --------
    >>> config = {"host": "localhost", "port": "5432"}
    >>> autoemit_config(Path("db.ini"), config, "Database")
    PosixPath('/home/user/db.ini')
    """
    try:
        func = EMISSION_REGISTRY[path.suffix]
    except KeyError:
        supported_extensions = ", ".join(EMISSION_REGISTRY.keys())
        raise KeyError(
            f"Unsupported file extension '{path.suffix}'. "
            f"Supported extensions are: {supported_extensions}"
        )
    if section is None:
        section = "DEFAULT"
    return func(path, section, configuration)


def register(
    *extensions: str
) -> typing.Callable[[typing.Callable], typing.Callable]:
    """
    Decorator to register configuration emitters for file extensions.
    
    Emitter functions should have the signature:
    (path: pathlib.Path, section: str, config: dict) -> pathlib.Path
    
    Parameters
    ----------
    *extensions : str
        File extensions to register (e.g., ".ini", ".toml", ".yaml").
        
    Returns
    -------
    callable
        Decorator function that registers the emitter.
        
    Examples
    --------
    >>> @register(".toml")
    ... def emit_toml(path, section, config):
    ...     import toml
    ...     data = {section: config}
    ...     with open(path, 'w') as f:
    ...         toml.dump(data, f)
    ...     return path.resolve()
    """
    def decoration(func: typing.Callable) -> typing.Callable:
        for extension in extensions:
            EMISSION_REGISTRY[extension] = func
        return func

    return decoration


@register(".ini", ".conf")
def emit_init(
    config_path: pathlib.Path,
    header: str,
    configuration: dict[typing.Any, typing.Any],
) -> pathlib.Path:
    """
    Emit configuration in INI format.
    
    Writes configuration data to an INI file with the specified section
    header. All configuration values are converted to strings as required
    by the INI format.
    
    Parameters
    ----------
    config_path : pathlib.Path
        Output path for the INI file.
    header : str
        Section name in the INI file (e.g., "[Database]").
    configuration : dict
        Key-value pairs to write under the section.
        
    Returns
    -------
    pathlib.Path
        Absolute path to the written configuration file.
        
    Notes
    -----
    - The path is expanded (~ -> home) and resolved to absolute form
    - Parent directories must exist or FileNotFoundError will be raised
    - Existing files will be overwritten
    
    Examples
    --------
    >>> config = {"host": "localhost", "port": "5432", "debug": "true"}
    >>> emit_init(Path("~/config.ini"), "Database", config)
    PosixPath('/home/user/config.ini')
    
    >>> # Results in:
    >>> # [Database]
    >>> # host = localhost
    >>> # port = 5432
    >>> # debug = true
    """
    parser = configparser.ConfigParser()
    parser[header] = configuration

    real_path = config_path.expanduser().resolve()
    with open(real_path, "wt") as fout:
        parser.write(fout)

    return real_path
