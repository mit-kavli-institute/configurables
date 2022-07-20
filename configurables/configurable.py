import os
import pathlib
import typing

from configurables.core import ConfigurationBuilder, ConfigurationFactory
from configurables.parse import PARSING_REGISTRY, autoparse_config


def configure(
    target: typing.Callable,
    config_path: typing.Union[str, bytes, os.PathLike],
    config_group: typing.Union[None, str] = None,
    extension_override: typing.Union[None, str] = None,
):
    path = pathlib.Path(config_path)

    if extension_override is not None:
        lookup = PARSING_REGISTRY[extension_override]
    else:
        lookup = autoparse_config(path, config_group)

    config = lookup(path, config_group)
    return target(**config)


def define_param(name, type):
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


def define_option(name, type, default=None):
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
    config_section, use_os_variables=False, use_cmd_line_variables=False
):
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
