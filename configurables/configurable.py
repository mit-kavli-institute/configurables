import os
import pathlib
import typing

import deal

from configurables.core import ConfigurationBuilder, ConfigurationFactory
from configurables.parse import PARSING_REGISTRY, autoparse_config


@deal.pre(lambda _: pathlib.Path(_.config_path).exists())
def configure(
    target: typing.Callable,
    config_path: typing.Union[str, bytes, os.PathLike],
    config_group: typing.Union[None, str] = None,
    extension_override: typing.Union[None, str] = None,
):
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
    else:
        lookup = autoparse_config(path, config_group)

    config = lookup(path, config_group)
    return target(**config)


@deal.pre(lambda _: len(_.name) > 0)
def define_param(name, type=str):
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
    >>> @define_param("username", type=str)
    >>> @define_param("password", type=str)
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


@deal.pre(lambda _: len(_.name) > 0)
def define_option(name, type, default=None):
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
    >>> @define_option("username", type=str, default=os.getlogin())
    >>> @define_param("password", type=str)
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


@deal.pre(lambda _: len(_.config_section) > 0)
def configurable(config_section):
    """
    The top-level decorator to fully bind a callable.

    Parameters
    ----------
    config_section: str, List[str]
        The configuration section to resolve parameters from.
    """

    def _internal(config_builder):
        if not isinstance(config_builder, ConfigurationBuilder):
            raise ValueError(
                "Wrapped function has not "
                "defined any parameters or options! "
                f"Instead got {config_builder}"
            )
        factory = ConfigurationFactory(config_builder, config_section)
        return factory

    return _internal
