import typing
from dataclasses import dataclass
from functools import partial

from configurables.emission import autoemit_config
from configurables.resolution import ResolutionDefinition


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
    def __init__(
        self,
        config_builder,
        section,
        configuration_order: ResolutionDefinition,
    ):
        self.builder = config_builder
        self.section = section
        self.configuration_order = configuration_order

    def __repr__(self):
        return f"{self.section}: {self.configuration_order}"

    def _resolve_param(self, key, raw_values):
        _type = self.builder.parameters[key].type
        value = raw_values[key]
        return _type(value)

    def _resolve_option(self, key, raw_values):
        _type = self.builder.options[key].type
        try:
            raw_value = raw_values[key]
        except KeyError:
            return self.builder.options[key].default

        return _type(raw_value)

    def parse(self, _filepath=None, _ignore_options=False, **overrides):
        context = {}
        if _filepath is not None:
            context["config_path"] = _filepath
        context["parse_kwargs"] = {"group": self.section}
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

    def __call__(self, _filepath=None, **overrides):
        kwargs = self.parse(_filepath=_filepath, **overrides)
        return self.builder.function(**kwargs)

    def emit(
        self, output_path, _filepath=None, _ignore_options=True, **overrides
    ):
        kwargs = self.parse(
            _filepath=_filepath, _ignore_options=_ignore_options, **overrides
        )
        return autoemit_config(output_path, kwargs, group=self.section)

    def partial(self, _filepath=None, **overrides):
        """
        Generate a partial function using the passed configurations.
        """
        kwargs = self.parse(_filepath=_filepath, **overrides)
        return partial(self.builder.function, **kwargs)
