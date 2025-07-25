from __future__ import annotations

import pathlib
from dataclasses import dataclass
from functools import partial
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Optional,
    TypeVar,
    Union,
    overload,
)

from configurables.emission import autoemit_config
from configurables.parse import ResolutionDefinition

# Type variables for generic support
T = TypeVar("T")  # Return type of the wrapped function
# When Python 3.10+ ParamSpec is available, we can use it for better parameter typing


@dataclass
class Parameter:
    """
    Represents a required configuration parameter.

    A parameter must be provided in the configuration source (file, environment
    variable, or command line) or as an override when calling the configured
    function.

    Attributes
    ----------
    name : str
        The name of the parameter as it appears in configuration sources.
    type : callable
        A callable that converts the string value from configuration to the
        desired type (e.g., int, float, pathlib.Path).

    Examples
    --------
    >>> param = Parameter(name="port", type=int)
    >>> param.type("8080")  # Converts string to int
    8080
    """
    name: str
    type: Callable


@dataclass
class Option:
    """
    Represents an optional configuration parameter with a default value.

    An option can be provided in configuration sources but will fall back to
    its default value if not found.

    Attributes
    ----------
    name : str
        The name of the option as it appears in configuration sources.
    type : callable
        A callable that converts the string value from configuration to the
        desired type.
    default : Any
        The default value to use if the option is not found in any
        configuration source.

    Examples
    --------
    >>> option = Option(name="timeout", type=int, default=30)
    >>> # If not in config, returns default
    >>> option.default
    30
    """
    name: str
    type: Callable
    default: Any


@dataclass
class ConfigurationBuilder(Generic[T]):
    """
    Builds configuration schema for a function.

    This class accumulates parameter and option definitions as decorators are
    applied to a function, building up a complete configuration schema.

    Attributes
    ----------
    parameters : dict
        Dictionary mapping parameter names to Parameter objects.
    options : dict
        Dictionary mapping option names to Option objects.
    function : callable
        The function that will be configured.
    """
    parameters: Dict[str, Parameter]
    options: Dict[str, Option]
    function: Callable[..., T]

    def add_parameter(self, name: str, type: Callable) -> Parameter:
        """
        Add a required parameter to the configuration schema.

        Parameters
        ----------
        name : str
            The name of the parameter.
        type : callable
            Type conversion function for the parameter.

        Returns
        -------
        Parameter
            The created Parameter object.
        """
        parameter = Parameter(name=name, type=type)
        self.parameters[name] = parameter

        return parameter

    def add_option(
        self,
        name: str,
        type: Callable,
        default: Optional[Any] = None,
    ) -> Option:
        """
        Add an optional parameter to the configuration schema.

        Parameters
        ----------
        name : str
            The name of the option.
        type : callable
            Type conversion function for the option.
        default : Any, optional
            Default value if the option is not found in configuration.

        Returns
        -------
        Option
            The created Option object.
        """
        option = Option(name=name, type=type, default=default)
        self.options[name] = option

        return option


class ConfigurationFactory(Generic[T]):
    """
    Factory for creating configured function instances.

    This class maintains the schema context when defining parameters and
    options. Using the maintained definition we are able to call the wrapped
    function, provide overrides, or emit template configurations.

    Attributes
    ----------
    builder : ConfigurationBuilder
        The configuration schema for the wrapped function.
    section : str
        Default configuration file section to use.
    configuration_order : ResolutionDefinition
        Defines the precedence order for configuration sources.

    Examples
    --------
    >>> # Created by @configurable decorator
    >>> @configurable("Settings")
    ... @param("value", type=int)
    ... def process(value):
    ...     return value * 2
    >>> # process is now a ConfigurationFactory
    >>> result = process("config.ini")
    """

    def __init__(
        self,
        config_builder: ConfigurationBuilder[T],
        section: str,
        configuration_order: ResolutionDefinition,
    ):
        """
        Initialize a ConfigurationFactory.

        Parameters
        ----------
        config_builder : ConfigurationBuilder
            The configuration schema.
        section : str
            Default configuration section name.
        configuration_order : ResolutionDefinition
            Resolution order for configuration sources.
        """
        self.builder = config_builder
        self.section = section
        self.configuration_order = configuration_order

    def __repr__(self) -> str:
        function = self.builder.function
        return repr(function)

    def _resolve_param(self, key: str, raw_values: dict) -> Any:
        """
        Resolve a parameter value with type conversion.

        Parameters
        ----------
        key : str
            Parameter name.
        raw_values : dict
            Raw configuration values.

        Returns
        -------
        Any
            Type-converted parameter value.

        Raises
        ------
        KeyError
            If the required parameter is not found.
        """
        _type = self.builder.parameters[key].type
        value = raw_values[key]
        return _type(value)

    def _resolve_option(self, key: str, raw_values: dict) -> Any:
        """
        Resolve an option value with type conversion or default.

        Parameters
        ----------
        key : str
            Option name.
        raw_values : dict
            Raw configuration values.

        Returns
        -------
        Any
            Type-converted option value or default if not found.
        """
        _type = self.builder.options[key].type
        try:
            raw_value = raw_values[key]
        except KeyError:
            return self.builder.options[key].default

        return _type(raw_value)

    @overload
    def __call__(
        self,
        _filepath: Union[str, pathlib.Path],
        _section: Optional[str] = None,
        **overrides: Any,
    ) -> T:
        """Call with configuration file."""
        ...

    @overload
    def __call__(
        self,
        _filepath: None = None,
        _section: None = None,
        **kwargs: Any,
    ) -> T:
        """Call with all parameters directly."""
        ...

    def __call__(
        self,
        _filepath: Optional[Union[str, pathlib.Path]] = None,
        _section: Optional[str] = None,
        **overrides: Any,
    ) -> T:
        """
        Call the wrapped function with configuration.

        Override __call__ protocol to allow transparent evocation of wrapped
        function.

        Parameters
        ----------
        _filepath : Optional[Union[str, pathlib.Path]]
            The filepath to the configuration file to use.
        _section : str, optional
            Override the configuration section to use. If left blank then
            the default provided during schema creation will be used.
        **overrides : Any
            Keyword overrides which will be used. Any keys provided here will
            override any configuration.

        Returns
        -------
        T
            The return value of the wrapped function.

        Examples
        --------
        >>> # Call with config file
        >>> result = configured_func("config.ini")
        >>> # Override section and values
        >>> result = configured_func("config.ini", _section="Dev", timeout=60)
        """
        if _filepath is not None:
            _filepath = pathlib.Path(_filepath)
        kwargs = self.parse(_section, _filepath=_filepath, **overrides)
        return self.builder.function(**kwargs)

    def parse(
        self,
        section: Optional[str],
        _filepath: Optional[pathlib.Path] = None,
        _ignore_options: bool = False,
        **overrides: Any,
    ) -> Dict[str, Any]:
        """
        Parse configuration from all sources.

        Given the schema configuration, parse any provided overrides, and load
        configurations from the relevant configuration file, environment
        variables, or command line definitions.

        Parameters
        ----------
        section : str
            The section to use against a provided configuration file.
        _filepath : pathlib.Path, optional
            An optional configuration file to pull values from.
        _ignore_options : bool, optional
            If true no defined options will be populated using configuration
            files, environment variables, or command line values. However
            keyword overrides will still affect any defined option.
            Default is False.
        **overrides : Any
            Override any keyword used by the wrapped function.

        Returns
        -------
        dict[str, Any]
            Dictionary of resolved configuration values ready to pass to the
            wrapped function.
        """
        context: Dict[str, Any] = {}
        if _filepath is not None:
            context["config_path"] = _filepath
        if section is None:
            section = self.section
        context["parse_kwargs"] = {"section": section}
        kwargs = {}
        parsed_opts = self.configuration_order.load(**context)
        for parameter in self.builder.parameters.keys():
            try:
                kwargs[parameter] = self._resolve_param(parameter, parsed_opts)
            except KeyError:
                kwargs[parameter] = overrides[parameter]

        if not _ignore_options:
            for option in self.builder.options.keys():
                kwargs[option] = self._resolve_option(option, parsed_opts)
        kwargs.update(overrides)
        return kwargs

    def emit(
        self,
        output_path: pathlib.Path,
        _section: Optional[str] = None,
        _filepath: Optional[pathlib.Path] = None,
        _ignore_options: bool = True,
        **overrides: Any,
    ) -> pathlib.Path:
        """
        Generate a configuration file template.

        Parameters
        ----------
        output_path : pathlib.Path
            Path where the configuration file will be written.
        _section : str, optional
            Configuration section name to use in the output file.
        _filepath : pathlib.Path, optional
            Existing configuration file to base values on.
        _ignore_options : bool, optional
            If True, only required parameters are included. Default is True.
        **overrides : Any
            Values to include in the generated configuration.

        Returns
        -------
        pathlib.Path
            Path to the generated configuration file.

        Examples
        --------
        >>> # Generate template with defaults
        >>> configured_func.emit("template.ini")
        >>> # Generate with specific values
        >>> configured_func.emit("template.ini", port=8080, debug=True)
        """
        kwargs = self.parse(
            _section,
            _filepath=_filepath,
            _ignore_options=_ignore_options,
            **overrides,
        )
        section = self.section if _section is None else _section
        return autoemit_config(output_path, kwargs, section=section)

    def partial(
        self,
        _filepath: Optional[pathlib.Path] = None,
        _section: Optional[str] = None,
        **overrides: Any,
    ) -> Callable[..., T]:
        """
        Generate a partial function using the passed configurations.

        Parameters
        ----------
        _filepath : pathlib.Path, optional
            Configuration file to load values from.
        _section : str, optional
            Configuration section to use.
        **overrides : Any
            Additional configuration overrides.

        Returns
        -------
        Callable[..., T]
            Partial function with configuration values pre-applied.

        Examples
        --------
        >>> # Create partial with config
        >>> partial_func = configured_func.partial("config.ini")
        >>> # Call multiple times with same config
        >>> result1 = partial_func()
        >>> result2 = partial_func()
        """
        kwargs = self.parse(_section, _filepath=_filepath, **overrides)
        return partial(self.builder.function, **kwargs)


def create_typed_wrapper(factory: ConfigurationFactory[T]) -> ConfigurationFactory[T]:
    """
    Create a typed wrapper for a ConfigurationFactory that preserves type information.

    This function enhances the factory with better type hints for IDE support,
    showing that configuration file inputs are valid alternatives to direct parameters.

    Parameters
    ----------
    factory : ConfigurationFactory[T]
        The configuration factory to wrap.

    Returns
    -------
    ConfigurationFactory[T]
        The same factory with enhanced type information.
    """
    # For now, we return the factory as-is since the type information
    # is already preserved through generics. In the future, we could
    # create a more sophisticated wrapper that generates dynamic signatures.
    return factory
