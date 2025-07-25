from __future__ import annotations

import os
import pathlib
import typing
from typing import Any, Callable, Optional, TypeVar, Union

from configurables.core import (
    ConfigurationBuilder,
    ConfigurationFactory,
    create_typed_wrapper,
)
from configurables.parse import (
    CFG,
    CLI,
    ENV,
    PARSING_REGISTRY,
    ResolutionDefinition,
    autoparse_config,
)

# Type variable for preserving function return types
T = TypeVar("T")


def configure(
    target: typing.Callable,
    config_path: typing.Union[str, os.PathLike],
    config_group: typing.Optional[str] = None,
    extension_override: typing.Optional[str] = None,
) -> typing.Callable:
    """
    A quick wrapper for configuring callables.
    
    This interface provides no type checking, default parameters, or os 
    environment/command overrides. Everything in the configuration file is 
    passed as is.

    Parameters
    ----------
    target : callable
        A callable to pass keyword arguments to.
    config_path : str or PathLike
        A path to a configuration file.
    config_group : str, optional
        The path to resolving to a desired group within the
        configuration object.
    extension_override : str, optional
        Parsing of configuration options happens by file extension. This
        allows a developer to override this behavior.
        
    Returns
    -------
    Any
        The result of calling target with the configuration as keyword arguments.
        
    Examples
    --------
    >>> def process(name, value):
    ...     return f"{name}: {value}"
    >>> result = configure(process, "config.ini", "Settings")
    """
    path = pathlib.Path(config_path)

    if extension_override is not None:
        lookup = PARSING_REGISTRY[extension_override]
        config = lookup(path, config_group)
    else:
        config = autoparse_config(path, config_group)

    return target(**config)


def param(name: str, type: Callable = str) -> Callable[[Union[ConfigurationBuilder[T], Callable[..., T]]], ConfigurationBuilder[T]]:
    """
    A decorator to add a required parameter to a ConfigurationBuilder.
    
    This functionality allows type casting to occur.

    Parameters
    ----------
    name : str
        The name (key) of the parameter.
    type : callable, optional
        The type to cast the parameter to. The default is str.
        
    Returns
    -------
    callable
        A decorator function that adds the parameter to the configuration.

    Examples
    --------
    >>> @configurable("Credentials")
    ... @param("username", type=str)
    ... @param("password", type=str)
    ... def login(username, password):
    ...     print(username, "*" * len(password))
    ...
    >>> login("credentials.ini")
    someusername **********
    """

    def _internal(
        obj: Union[ConfigurationBuilder[T], Callable[..., T]]
    ) -> ConfigurationBuilder[T]:
        if isinstance(obj, ConfigurationBuilder):
            config_builder = obj
        else:
            # Assume that we're decorating the target callable
            config_builder = ConfigurationBuilder[T](
                parameters={}, options={}, function=obj
            )
        config_builder.add_parameter(name=name, type=type)
        return config_builder

    return _internal


def option(
    name: str, type: Callable = str, default: Any = None
) -> Callable[[Union[ConfigurationBuilder[T], Callable[..., T]]], ConfigurationBuilder[T]]:
    """
    A decorator to add an optional parameter to a ConfigurationBuilder.
    
    This functionality allows type casting to occur as well as providing a default
    value. This default value is *not* type checked.

    Parameters
    ----------
    name : str
        The name (key) of the option.
    type : callable, optional
        The type to cast the option. This cast will *not* be applied to
        provided defaults. Default is str.
    default : Any, optional
        The default value to provide if it is not found within the config
        file, os environments, or overrides. Default is None.
        
    Returns
    -------
    callable
        A decorator function that adds the option to the configuration.

    Examples
    --------
    >>> import os
    >>> @configurable("Credentials")
    ... @option("username", type=str, default=os.getlogin())
    ... @param("password", type=str)
    ... def login(username, password):
    ...     print(username, "*" * len(password))
    ...
    >>> login("credentials.ini")
    willfong ***********
    """

    def _internal(
        obj: Union[ConfigurationBuilder[T], Callable[..., T]]
    ) -> ConfigurationBuilder[T]:
        if isinstance(obj, ConfigurationBuilder):
            config_builder = obj
        else:
            # Assume that we're decorating the target callable
            config_builder = ConfigurationBuilder[T](
                parameters={}, options={}, function=obj
            )
        config_builder.add_option(name=name, type=type, default=default)
        return config_builder

    return _internal


def configurable(
    config_section: Optional[str] = None,
    order: Optional[ResolutionDefinition] = None,
) -> Callable[[ConfigurationBuilder[T]], ConfigurationFactory[T]]:
    """
    The top-level decorator to fully bind a callable.

    Parameters
    ----------
    config_section : str, optional
        The configuration section to resolve parameters from. If left
        blank, it will be up to the callee to provide a section during
        runtime.
    order : ResolutionDefinition, optional
        Custom resolution order for configuration sources. If not provided,
        the default order is CLI > CFG > ENV.
        
    Returns
    -------
    callable
        A decorator function that returns a ConfigurationFactory.
        
    Raises
    ------
    ValueError
        If the wrapped function has not defined any parameters or options.
        
    Examples
    --------
    >>> @configurable("Settings")
    ... @param("value", type=int)
    ... def process(value):
    ...     return value * 2
    ...
    >>> # Can customize resolution order
    >>> @configurable("Settings", order=ENV > CFG > CLI)
    ... @param("value", type=int)
    ... def process_env_first(value):
    ...     return value
    """

    def _internal(
        config_builder: ConfigurationBuilder[T]
    ) -> ConfigurationFactory[T]:
        if not isinstance(config_builder, ConfigurationBuilder):
            raise ValueError(
                "Wrapped function has not "
                "defined any parameters or options! "
                f"Instead got {config_builder}"
            )
        # Default order is CLI > CFG > ENV
        default_order = CLI > CFG > ENV
        factory = ConfigurationFactory[T](
            config_builder,
            config_section or "DEFAULT",
            default_order if order is None else order
        )
        # Return the factory with enhanced typing
        return create_typed_wrapper(factory)

    return _internal
