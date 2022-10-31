import configparser
import operator
import os
import pathlib
import sys
import typing

import deal

from configurables.resolution import ResolutionDefinition

PARSING_REGISTRY = {}  # type: typing.Dict[str, typing.Any]


def autoparse_config(path: pathlib.Path, group=None) -> dict:
    global PARSING_REGISTRY
    func = PARSING_REGISTRY[path.suffix]
    if group is None:
        return func(path)
    return func(path, group)


def register(*extensions):
    def decoration(func):
        global PARSING_REGISTRY
        for extension in extensions:
            PARSING_REGISTRY[extension] = func
        return func

    return decoration


@deal.raises(KeyError)
@deal.pre(lambda _: _.config_path.exists())
@deal.pre(lambda _: isinstance(_.config_path, pathlib.Path))
@deal.pure
@register(".ini", ".conf")
def parse_ini(config_path: pathlib.Path, key: str):
    """Parse an ini file.
    Parameters
    ----------
    config_path: pathlib.Path
        The path to the desired ini configuration file
    key: str
        The group of the ini file to read in as keyword arguments
    """
    config = configparser.ConfigParser()
    config.read(config_path)
    established_keys = config.sections()
    if key not in established_keys:
        established_keys = config.sections()
        raise KeyError(
            f"Could not find section '{key}', "
            f"only found [{', '.join(established_keys)}]"
        )
    return config[key]


RHS = typing.Union[ResolutionDefinition, "Interpreter"]


class Interpreter:
    name: typing.Union[str, None] = None

    def load(self, **context):
        return self.interpret(context)

    def interpret(self, context):
        raise NotImplementedError

    def _coalese(self, rhs, op):
        if isinstance(rhs, ResolutionDefinition):
            lhs = self
        else:
            lhs = ResolutionDefinition(self)
        return op(lhs, rhs)

    def __lt__(self, rhs: RHS):
        return self._coalese(rhs, operator.lt)

    def __gt__(self, rhs: RHS):
        return self._coalese(rhs, operator.gt)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class Env(Interpreter):
    name = "ENV"

    def interpret(self, context):
        return os.environ


class Cli(Interpreter):
    name = "CLI"

    def interpret(self, context):
        args = sys.argv
        nargs = len(args)
        cursor = 1
        accumulator = {}
        while cursor < nargs:
            arg = args[cursor]
            if arg.startswith("--"):
                param_name = arg[2:]
                accumulator[param_name] = None

                cursor += 1
                while cursor < nargs and not args[cursor].startswith("--"):
                    arg = args[cursor]
                    current_val = accumulator[param_name]
                    if current_val is None:
                        accumulator[param_name] = arg
                    elif isinstance(current_val, str):
                        accumulator[param_name] = [current_val, arg]
                    else:
                        accumulator[param_name].append(arg)
                    cursor += 1
        return accumulator


class Cfg(Interpreter):
    name = "CFG"

    def interpret(self, context):
        config_path = context["config_path"]
        result = autoparse_config(
            config_path, **context.get("parse_kwargs", {})
        )
        return result


ENV = Env()
CLI = Cli()
CFG = Cfg()
