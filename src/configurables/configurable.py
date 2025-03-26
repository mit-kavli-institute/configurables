from __future__ import annotations

import os
import pathlib
import typing

from configurables.core import ConfigurationBuilder, ConfigurationFactory
from configurables.parse import (
    CFG,
    PARSING_REGISTRY,
    ResolutionDefinition,
    autoparse_config,
)


def configure(
    target: typing.Callable,
    config_path: typing.Union[str, os.PathLike],
    config_group: typing.Optional[str] = None,
    extension_override: typing.Optional[str] = None,
) -> typing.Callable:
    """
    A quick wrapper for configuring callables. This interface provides no
    type checking, default parameters, or os envrionment/command overrides.
    Everything in the configuration file is passed as is.

    Parameters
    ----------
    target: callable
        A callable to pass keyword arguments to.
    config_path: pathlike
        A path to a configuration file
    config_group: str
        The path to resolving to a desired group within the
        configuration object.
    extension_override: str, optional
        Parsing of configuration options happens by file extension. This
        allows a developer to override this behavior.
    """
    path = pathlib.Path(config_path)

    if extension_override is not None:
        lookup = PARSING_REGISTRY[extension_override]
        config = lookup(path, config_group)
    else:
        config = autoparse_config(path, config_group)

    return target(**config)


def param(name: str, type=str) -> typing.Callable:
    """
    A decorator to add a required parameter to a ConfigurationBuilder. This
    functionality allows type casting to occur.

    Parameters
    ----------
    name: str
        The name (key) of the parameter.
    type: callable, optional
        The type to cast the parameter to. The default is str.

    Examples
    --------
    >>> @configurable("Credentials")
    >>> @param("username", type=str)
    >>> @param("password", type=str)
    >>> def login(username, password):
    >>>     print(username, "*" * len(password))
    >>>
    >>> login("credentials.ini")
    ('someusername', '**********')
    """

    def _internal(obj):
        if isinstance(obj, ConfigurationBuilder):
            config_builder = obj
        else:
            # Assume that we're decorating the target callable
            config_builder = ConfigurationBuilder(
                parameters={}, options={}, function=obj
            )
        config_builder.add_parameter(name=name, type=type)
        return config_builder

    return _internal


def option(name: str, type=str, default: typing.Any = None) -> typing.Callable:
    """
    A decorator to add an optional parameter to a ConfigurationBuilder. This
    functionality allows type casting to occur as well as providing a default
    value. This default value is *not* type checked.

    Parameters
    ----------
    name: str
        The name (key) of the option.
    type: callable, optional
        The type to cast the option. This cast will *not* be applied to
        provided defaults.
    default: any, optional
        The default value to provide if it is not found within the config
        file, os environments, or overrides. By default, this default is
        None.

    Examples
    --------
    >>> @configurable("Credentials")
    >>> @option("username", type=str, default=os.getlogin())
    >>> @param("password", type=str)
    >>> def login(username, password):
    >>>     print(username, "*" * len(password))
    >>>
    >>> login("credentials.ini")
    ('willfong', '***********')
    """

    def _internal(obj):
        if isinstance(obj, ConfigurationBuilder):
            config_builder = obj
        else:
            # Assume that we're decorating the target callable
            config_builder = ConfigurationBuilder(
                parameters={}, options={}, function=obj
            )
        config_builder.add_option(name=name, type=type, default=default)
        return config_builder

    return _internal


def configurable(
    config_section: typing.Optional[str] = None,
    order: typing.Optional[ResolutionDefinition] = None,
) -> typing.Callable:
    """
    The top-level decorator to fully bind a callable.

    Parameters
    ----------
    config_section: str, optional
        The configuration section to resolve parameters from. If left
        blank, it will be up to the callee to provide a section during
        runtime.
    """

    def _internal(config_builder):
        if not isinstance(config_builder, ConfigurationBuilder):
            raise ValueError(
                "Wrapped function has not "
                "defined any parameters or options! "
                f"Instead got {config_builder}"
            )
        factory = ConfigurationFactory(
            config_builder, config_section, CFG if order is None else order
        )
        return factory

    return _internal
