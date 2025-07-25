"""
Configuration parsing and resolution module.

This module provides the infrastructure for loading configuration from multiple
sources (environment variables, command-line arguments, configuration files)
with customizable precedence ordering.

The module implements:
- A flexible precedence system using overloaded operators (>, <)
- Pluggable interpreters for different configuration sources
- A registry system for configuration file parsers
- Default parsers for INI/CONF file formats

Classes
-------
InvalidOrdering
    Exception raised for invalid configuration source orderings.
ResolutionDefinition
    Manages precedence ordering of configuration sources.
Interpreter
    Abstract base class for configuration source interpreters.
Env
    Interpreter for environment variables.
Cli
    Interpreter for command-line arguments.
Cfg
    Interpreter for configuration files.

Functions
---------
autoparse_config
    Automatically parse a configuration file based on extension.
register
    Decorator to register file format parsers.
parse_ini
    Parse INI/CONF configuration files.

Examples
--------
>>> # Default ordering: CLI > CFG > ENV
>>> from configurables.parse import CLI, CFG, ENV
>>> order = CLI > CFG > ENV

>>> # Custom ordering with environment variables first
>>> order = ENV > CLI > CFG

>>> # Register a custom parser
>>> @register('.json')
... def parse_json(path, section=None):
...     import json
...     with open(path) as f:
...         return json.load(f)
"""

from __future__ import annotations

import configparser
import operator
import os
import pathlib
import sys
import typing

# Optional dependencies for YAML and TOML support
try:
    import yaml  # type: ignore[import-untyped]

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    # Python 3.11+ has tomllib in standard library
    import tomllib

    HAS_TOML = True
except ImportError:
    try:
        # For older Python versions, try tomli
        import tomli as tomllib  # type: ignore[import-not-found]

        HAS_TOML = True
    except ImportError:
        HAS_TOML = False

PARSING_REGISTRY = {}  # type: typing.Dict[str, typing.Any]

RHS = typing.Union["ResolutionDefinition", "Interpreter"]
LHS = RHS
OP = typing.Callable[[LHS, RHS], "ResolutionDefinition"]


class InvalidOrdering(Exception):
    """
    Raised when configuration source ordering contains cycles or duplicates.

    This exception is raised when attempting to create a ResolutionDefinition
    with an invalid ordering, such as circular dependencies or duplicate
    sources.

    Examples
    --------
    >>> # These would raise InvalidOrdering:
    >>> ENV > ENV  # Duplicate source
    >>> ENV > CFG > ENV  # Circular dependency

    Notes
    -----
    Valid orderings must form a linear precedence chain without repetition.
    """

    pass


class ResolutionDefinition:
    """
    Manages precedence ordering of configuration sources.

    This class defines how different configuration sources (CLI, environment
    variables, config files) are prioritized when resolving values. It uses
    overloaded comparison operators (> and <) to create intuitive ordering
    syntax.

    Attributes
    ----------
    interpreter_order : list
        Ordered list of Interpreter instances, from highest to lowest
        precedence.

    Examples
    --------
    >>> import configurables as conf
    >>> # Environment variables take precedence over config files
    >>> @conf.configurable("Test", order=conf.ENV > conf.CFG)
    ... @conf.param("key", type=str)
    ... def load(key):
    ...     print(key)

    >>> # Custom three-way precedence
    >>> order = conf.CLI > conf.ENV > conf.CFG

    Notes
    -----
    The default ordering is CLI > CFG > ENV, meaning command-line arguments
    have highest precedence, followed by config files, then environment
    variables.
    """

    def __init__(self, first_element: "RHS"):
        """
        Initialize with a single configuration source.

        Parameters
        ----------
        first_element : RHS
            The initial Interpreter or ResolutionDefinition in the chain.
        """
        self.interpreter_order = [first_element]

    def __lt__(self, rhs: "RHS") -> "ResolutionDefinition":
        """
        Add a higher precedence source to the chain.

        Parameters
        ----------
        rhs : RHS
            Configuration source to add with higher precedence.

        Returns
        -------
        ResolutionDefinition
            Self for method chaining.

        Raises
        ------
        InvalidOrdering
            If rhs is already in the ordering chain.
        """
        if rhs in self.interpreter_order:
            raise InvalidOrdering()

        self.interpreter_order.insert(0, rhs)
        return self

    def __gt__(self, rhs: "RHS") -> "ResolutionDefinition":
        """
        Add a lower precedence source to the chain.

        Parameters
        ----------
        rhs : RHS
            Configuration source to add with lower precedence.

        Returns
        -------
        ResolutionDefinition
            Self for method chaining.

        Raises
        ------
        InvalidOrdering
            If rhs is already in the ordering chain.
        """
        if rhs in self.interpreter_order:
            raise InvalidOrdering()

        self.interpreter_order.append(rhs)
        return self

    def load(self, **context: typing.Any) -> dict:
        """
        Load configuration from all sources in precedence order.

        Values from higher precedence sources override those from lower
        precedence sources.

        Parameters
        ----------
        **context : Any
            Context information passed to interpreters, such as:
            - config_path: Path to configuration file
            - parse_kwargs: Additional parsing arguments

        Returns
        -------
        dict
            Merged configuration with precedence rules applied.
        """
        payload = {}

        for interpreter in self.interpreter_order:
            kwargs = interpreter.load(**context)
            payload.update(kwargs)

        return payload


def autoparse_config(
    path: pathlib.Path, section: typing.Optional[str] = None
) -> dict:
    """
    Automatically parse a configuration file based on its extension.

    This function looks up the appropriate parser in the PARSING_REGISTRY
    based on the file extension and uses it to parse the configuration.

    Parameters
    ----------
    path : pathlib.Path
        Path to the configuration file.
    section : str, optional
        Section within the configuration file to parse. If None, the
        default section is used.

    Returns
    -------
    dict
        Parsed configuration as key-value pairs.

    Notes
    -----
    Falls back to .ini parser if the file extension is not registered.
    """
    path = pathlib.Path(path).expanduser()
    func = PARSING_REGISTRY.get(path.suffix, PARSING_REGISTRY[".ini"])
    if section is None:
        return func(path)
    return func(path, section)


def register(
    *extensions: str,
) -> typing.Callable[[typing.Callable], typing.Callable]:
    """
    Decorator to register a parser function for file extensions.

    Parameters
    ----------
    *extensions : str
        File extensions to register (e.g., ".ini", ".json", ".yaml").

    Returns
    -------
    callable
        Decorator function that registers the parser.

    Examples
    --------
    >>> @register(".json")
    ... def parse_json(path, section=None):
    ...     with open(path) as f:
    ...         data = json.load(f)
    ...     return data.get(section, data) if section else data
    """

    def decoration(func: typing.Callable) -> typing.Callable:
        for extension in extensions:
            PARSING_REGISTRY[extension] = func
        return func

    return decoration


@register(".ini", ".conf")
def parse_ini(
    config_path: pathlib.Path, key: str
) -> configparser.SectionProxy:
    """
    Parse an INI configuration file.

    Parameters
    ----------
    config_path : pathlib.Path
        Path to the INI configuration file.
    key : str
        Section name within the INI file to parse.

    Returns
    -------
    configparser.SectionProxy
        Dictionary-like object containing the section's key-value pairs.

    Raises
    ------
    KeyError
        If the specified section is not found in the configuration file.
        The error message includes available sections and file contents
        for debugging (be careful with sensitive data).

    Examples
    --------
    >>> # Parse the [database] section from config.ini
    >>> config = parse_ini(Path("config.ini"), "database")
    >>> host = config["host"]
    >>> port = int(config["port"])
    """
    config = configparser.ConfigParser()
    expanded = config_path.expanduser()
    config.read(expanded)
    established_keys = config.sections()
    if key not in established_keys:
        established_keys = config.sections()
        content = open(expanded, "rt").read()
        raise KeyError(
            f"Could not find section '{key}', "
            f"only found [{', '.join(established_keys)}]."
            f"Config File: {config_path}\n"
            "---POTENTIALLY PRINTED SECRETS---\n"
            "Please review before copy-paste!\n"
            f"{content}"
            "---END CONFIG CONTENT---"
        )
    return config[key]


@register(".yaml", ".yml")
def parse_yaml(config_path: pathlib.Path, key: str) -> dict:
    """
    Parse a YAML configuration file.

    Parameters
    ----------
    config_path : pathlib.Path
        Path to the YAML configuration file.
    key : str
        Section name within the YAML file to parse.

    Returns
    -------
    dict
        Dictionary containing the section's key-value pairs.

    Raises
    ------
    ImportError
        If PyYAML is not installed.
    KeyError
        If the specified section is not found in the configuration file.
        The error message includes available sections and file contents
        for debugging (be careful with sensitive data).

    Examples
    --------
    >>> # Parse the 'database' section from config.yaml
    >>> config = parse_yaml(Path("config.yaml"), "database")
    >>> host = config["host"]
    >>> port = int(config["port"])
    """
    if not HAS_YAML:
        raise ImportError(
            "PyYAML is required for YAML parsing. "
            "Install it with: pip install PyYAML"
        )

    expanded = config_path.expanduser()
    with open(expanded, "r") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(
            f"YAML file must contain a dictionary at top level, "
            f"got {type(data).__name__}"
        )

    if key not in data:
        established_keys = list(data.keys())
        with open(expanded, "rt") as file:
            content = file.read()
        raise KeyError(
            f"Could not find section '{key}', "
            f"only found [{', '.join(established_keys)}]."
            f"Config File: {config_path}\n"
            "---POTENTIALLY PRINTED SECRETS---\n"
            "Please review before copy-paste!\n"
            f"{content}"
            "---END CONFIG CONTENT---"
        )

    return data[key]


@register(".toml")
def parse_toml(config_path: pathlib.Path, key: str) -> dict:
    """
    Parse a TOML configuration file.

    Parameters
    ----------
    config_path : pathlib.Path
        Path to the TOML configuration file.
    key : str
        Section name within the TOML file to parse.

    Returns
    -------
    dict
        Dictionary containing the section's key-value pairs.

    Raises
    ------
    ImportError
        If tomllib/tomli is not installed (for Python < 3.11).
    KeyError
        If the specified section is not found in the configuration file.
        The error message includes available sections and file contents
        for debugging (be careful with sensitive data).

    Examples
    --------
    >>> # Parse the 'database' section from config.toml
    >>> config = parse_toml(Path("config.toml"), "database")
    >>> host = config["host"]
    >>> port = config["port"]
    """
    if not HAS_TOML:
        raise ImportError(
            "tomllib is required for TOML parsing. "
            "For Python < 3.11, install tomli with: pip install tomli"
        )

    expanded = config_path.expanduser()
    with open(expanded, "rb") as f:
        data = tomllib.load(f)

    if key not in data:
        established_keys = list(data.keys())
        with open(expanded, "rt") as file:
            content = file.read()
        raise KeyError(
            f"Could not find section '{key}', "
            f"only found [{', '.join(established_keys)}]."
            f"Config File: {config_path}\n"
            "---POTENTIALLY PRINTED SECRETS---\n"
            "Please review before copy-paste!\n"
            f"{content}"
            "---END CONFIG CONTENT---"
        )

    return data[key]


class Interpreter:
    """
    Abstract base class for configuration source interpreters.

    Interpreters are responsible for loading configuration from specific
    sources (environment variables, command line, config files, etc.).

    Attributes
    ----------
    name : str, optional
        Human-readable name of the interpreter for debugging.

    Notes
    -----
    Subclasses must implement the interpret() method to define how
    configuration is loaded from their specific source.
    """

    name: typing.Optional[str] = None

    def load(self, **context: typing.Any) -> dict:
        """
        Load configuration from this source.

        Parameters
        ----------
        **context : Any
            Context information for loading configuration.

        Returns
        -------
        dict
            Configuration key-value pairs.
        """
        return self.interpret(context)

    def interpret(self, context: dict) -> dict:
        """
        Extract configuration from the source.

        Parameters
        ----------
        context : dict
            Context information for interpretation.

        Returns
        -------
        dict
            Configuration key-value pairs.

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses.
        """
        raise NotImplementedError

    def _coalese(self, rhs: RHS, op: OP) -> ResolutionDefinition:
        """
        Coalesce interpreter into ResolutionDefinition.

        Parameters
        ----------
        rhs : RHS
            Right-hand side of the operation.
        op : OP
            Operator function to apply.

        Returns
        -------
        ResolutionDefinition
            Resolution definition with ordering applied.
        """
        if isinstance(rhs, ResolutionDefinition):
            lhs = self  # type: LHS
        else:
            lhs = ResolutionDefinition(self)
        return op(lhs, rhs)

    def __lt__(self, rhs: RHS) -> ResolutionDefinition:
        """
        Create ordering with self as lower precedence than rhs.

        Parameters
        ----------
        rhs : RHS
            Higher precedence source.

        Returns
        -------
        ResolutionDefinition
            Ordering with rhs > self.
        """
        return self._coalese(rhs, operator.lt)

    def __gt__(self, rhs: RHS) -> ResolutionDefinition:
        """
        Create ordering with self as higher precedence than rhs.

        Parameters
        ----------
        rhs : RHS
            Lower precedence source.

        Returns
        -------
        ResolutionDefinition
            Ordering with self > rhs.
        """
        return self._coalese(rhs, operator.gt)

    def __str__(self) -> str:
        """
        Return string representation.

        Returns
        -------
        str
            The interpreter's name or "Unknown".
        """
        return self.name or "Unknown"

    def __repr__(self) -> str:
        """
        Return detailed string representation.

        Returns
        -------
        str
            The interpreter's name or "Unknown".
        """
        return self.name or "Unknown"


class Env(Interpreter):
    """
    Interpreter for environment variables.

    Loads all environment variables as configuration values.
    """

    name = "ENV"

    def interpret(self, context: dict) -> dict:
        """
        Load all environment variables.

        Parameters
        ----------
        context : dict
            Not used by this interpreter.

        Returns
        -------
        dict
            All environment variables as key-value pairs.
        """
        return dict(os.environ)


class Cli(Interpreter):
    """
    Interpreter for command-line arguments.

    Parses command-line arguments in the format --key value. Supports
    multiple values for the same key, which are collected into a list.

    Examples
    --------
    >>> # Single value: --port 8080
    >>> # Multiple values: --server host1 --server host2
    >>> # Flag without value: --debug
    """

    name = "CLI"

    def interpret(self, context: dict) -> dict:
        """
        Parse command-line arguments.

        Parameters
        ----------
        context : dict
            Not used by this interpreter.

        Returns
        -------
        dict
            Parsed command-line arguments where:
            - Single values are strings
            - Multiple values for same key become lists
            - Flags without values are None
        """
        args = sys.argv
        nargs = len(args)
        cursor = 1
        accumulator = {}  # type: dict[str, typing.Union[str, list[str], None]]
        while cursor < nargs:
            arg = args[cursor]
            if arg.startswith("--"):
                param_name = arg[2:]
                accumulator[param_name] = None

                cursor += 1
                while cursor < nargs and not args[cursor].startswith("--"):
                    arg = args[cursor]
                    current_val = accumulator[param_name]
                    if isinstance(current_val, str):
                        accumulator[param_name] = [current_val, arg]
                    elif isinstance(current_val, list):
                        current_val.append(arg)
                    elif current_val is None:
                        accumulator[param_name] = arg
                    cursor += 1
        return accumulator


class Cfg(Interpreter):
    """
    Interpreter for configuration files.

    Loads configuration from files using the appropriate parser based on
    file extension. Requires 'config_path' in context.
    """

    name = "CFG"

    def interpret(self, context: dict) -> dict:
        """
        Load configuration from file.

        Parameters
        ----------
        context : dict
            Must contain:
            - config_path: Path to configuration file
            - parse_kwargs (optional): Additional parsing arguments

        Returns
        -------
        dict
            Parsed configuration or empty dict if no config_path provided.
        """
        try:
            config_path = context["config_path"]
        except KeyError:
            return {}

        result = autoparse_config(
            config_path, **context.get("parse_kwargs", {})
        )
        return result


ENV = Env()
CLI = Cli()
CFG = Cfg()
