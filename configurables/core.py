from __future__ import annotations

import pathlib
import typing
from dataclasses import dataclass
from functools import partial

from configurables.emission import autoemit_config
from configurables.parse import ResolutionDefinition


@dataclass
class Parameter:
    name: str
    type: typing.Callable


@dataclass
class Option:
    name: str
    type: typing.Callable
    default: typing.Any


@dataclass
class ConfigurationBuilder:
    parameters: dict
    options: dict
    function: typing.Callable

    def add_parameter(self, name: str, type: typing.Callable) -> Parameter:
        parameter = Parameter(name=name, type=type)
        self.parameters[name] = parameter

        return parameter

    def add_option(
        self,
        name: str,
        type: typing.Callable,
        default: typing.Optional[typing.Any] = None,
    ) -> Option:
        option = Option(name=name, type=type, default=default)
        self.options[name] = option

        return option


class ConfigurationFactory:
    def __init__(
        self,
        config_builder: ConfigurationBuilder,
        section: str,
        configuration_order: ResolutionDefinition,
    ):
        self.builder = config_builder
        self.section = section
        self.configuration_order = configuration_order

    def __repr__(self):
        function = self.builder.function
        return repr(function)

    def _resolve_param(self, key: str, raw_values: dict) -> typing.Any:
        _type = self.builder.parameters[key].type
        value = raw_values[key]
        return _type(value)

    def _resolve_option(self, key: str, raw_values: dict) -> typing.Any:
        _type = self.builder.options[key].type
        try:
            raw_value = raw_values[key]
        except KeyError:
            return self.builder.options[key].default

        return _type(raw_value)

    def __call__(
        self,
        _filepath: typing.Optional[pathlib.Path] = None,
        _section: typing.Optiona[str] = None,
        **overrides: typing.Any,
    ) -> typing.Any:
        kwargs = self.parse(_section, _filepath=_filepath, **overrides)
        return self.builder.function(**kwargs)

    def parse(
        self,
        section,
        _filepath: typing.Optional[pathlib.Path] = None,
        _ignore_options: bool = False,
        **overrides: typing.Any,
    ) -> typing.Any:
        context = {}  # type: typing.Dict[str, typing.Any]
        if _filepath is not None:
            context["config_path"] = _filepath
        if section is None:
            section = self.section
        context["parse_kwargs"] = {"group": section}
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
        _section: typing.Optional[str] = None,
        _filepath: typing.Optional[pathlib.Path] = None,
        _ignore_options: bool = True,
        **overrides: typing.Any,
    ) -> dict:
        kwargs = self.parse(
            _section,
            _filepath=_filepath,
            _ignore_options=_ignore_options,
            **overrides,
        )
        section = self.section if _section is None else _section
        return autoemit_config(output_path, kwargs, group=section)

    def partial(
        self,
        _filepath: typing.Optional[pathlib.Path] = None,
        _section: typing.Optional[str] = None,
        **overrides: typing.Any,
    ) -> typing.Callable:
        """
        Generate a partial function using the passed configurations.
        """
        kwargs = self.parse(_section, _filepath=_filepath, **overrides)
        return partial(self.builder.function, **kwargs)
