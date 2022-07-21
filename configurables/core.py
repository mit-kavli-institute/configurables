"""Docstring for the core.py module.

This module constructs the common datastructures used by configurables.

"""

import os
import pathlib
import typing
from dataclasses import dataclass

import deal

from configurables.parse import parse_ini


@dataclass
class Parameter:
    """
    A 'required' configuration parameter. When resolving from different
    configurations, a parameter must, in the end, have a defined value.

    Attributes
    ----------
    name : str
        The 'name' of the parameter or the key used within a configuration.
    type : callable
        The type to cast the resolved parameter to. It must be a callable
        that accepts a single positional parameter.

    Notes
    -----
    If resolving using TOML, YAML, JSON, or any other "typed" configuration
    schema, resolving types will result in duplicate when casting types.
    """

    name: str
    type: typing.Callable


@dataclass
class Option(Parameter):
    """
    An 'optional' configuration parameter. When resovling from different
    configurations, an option if not found within any of the specified
    configurations will have the provided default be its value.

    Attributes
    ----------
    name : str
        The 'name' of the parameter or the key used within a configuration.
    type : callable
        The type to cast the resolved parameter to. It must be a callable
        that accepts a single positional parameter.
    default
        The default value to return if this parameter is not found within any
        configuration. This value is *not* casted using the provided type.

    Notes
    -----
    If resolving using TOML, YAML, JSON, or any other "typed" configuration
    schema, resolving types will result in duplicate when casting types.

    The provided default value will not be type casted!

    """

    default: typing.Any


@dataclass
class ConfigurationBuilder:
    """
    A stateful collection of parameters and options. This class is primarily
    used by the front-facing decorators to maintain state.

    Attributes
    ----------
    parameters : dict
        A dictionary resolving a name to a parameter.
    options : dict
        A dictionary resolving a name to an option.
    function : callable
        The wrapped function to provide arguments for.

    Methods
    -------
    add_parameter(name, type)
        Add a new parameter to look for when resolving configurations.
    add_option(name, type, default=None)
        Add a new option to look for when resolving configurations, using
        ``default`` when the option is not found.
    """

    parameters: typing.Dict
    options: typing.Dict
    function: typing.Callable

    @deal.pre(lambda _: len(_.name) > 0)
    def add_parameter(self, name, type):
        parameter = Parameter(name=name, type=type)
        self.parameters[name] = parameter

    @deal.pre(lambda _: len(_.name) > 0)
    def add_option(self, name, type, default=None):
        option = Option(name=name, type=type, default=default)
        self.options[name] = option


class ConfigurationFactory:
    """
    A factory class for generating keyword arguments by reading in various
    configuration sources.

    Attributes
    ----------
    builder : ConfigurationBuilder
        The parameter datastructure to pass configurations through to resolve
        values.
    section : str or List[str]
        The section or path to the configuration group within passed
        configuration files.

    Methods
    -------
    parse(filepath, **overrides)
        Parse the provided filepath for values.

    __call__(config_path, **overrides)
        Call the wrapped function.
    """

    def __init__(self, config_builder, section):
        self.builder = config_builder
        self.section = section

    @deal.pure
    def _resolve_param(self, key, file_opts, overrides):
        _type = self.builder.parameters[key].type
        return _type(overrides.get(key, os.environ.get(key, file_opts[key])))

    @deal.pure
    def _resolve_option(self, key, file_opts, overrides):
        _type = self.builder.options[key].type
        return _type(
            overrides.get(
                key,
                os.environ.get(
                    key, file_opts.get(key, self.builder.options[key].default)
                ),
            )
        )

    @deal.pre(lambda _: pathlib.Path(_.filepath).exists())
    def parse(self, filepath, **overrides):
        kwargs = {}
        file_opts = parse_ini(filepath, self.section)
        for parameter in self.builder.parameters.keys():
            kwargs[parameter] = self._resolve_param(
                parameter, file_opts, overrides
            )
        for option in self.builder.options.keys():
            kwargs[option] = self._resolve_option(option, file_opts, overrides)
        return kwargs

    @deal.pre(lambda _: pathlib.Path(_.filepath).exists())
    def __call__(self, filepath, **overrides):
        path = pathlib.Path(filepath)
        kwargs = self.parse(path, **overrides)
        return self.builder.function(**kwargs)
