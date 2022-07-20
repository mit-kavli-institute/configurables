import os
import pathlib
import typing
from dataclasses import dataclass

import deal

from configurables.parse import parse_ini


@dataclass
class Parameter:
    name: str
    type: typing.Callable


@dataclass
class Option(Parameter):
    default: typing.Any


@dataclass
class ConfigurationBuilder:
    parameters: typing.Dict
    options: typing.Dict
    function: typing.Callable

    def add_parameter(self, name, type):
        parameter = Parameter(name=name, type=type)
        self.parameters[name] = parameter

    def add_option(self, name, type, default=None):
        option = Option(name=name, type=type, default=default)
        self.options[name] = option


class ConfigurationFactory:
    def __init__(self, config_builder, section):
        self.builder = config_builder
        self.section = section

    def _resolve_param(self, key, file_opts, overrides):
        _type = self.builder.parameters[key].type
        return _type(overrides.get(key, os.environ.get(key, file_opts[key])))

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
