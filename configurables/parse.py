from __future__ import annotations

import configparser
import operator
import os
import pathlib
import sys
import typing

PARSING_REGISTRY = {}  # type: typing.Dict[str, typing.Any]

RHS = typing.Union["ResolutionDefinition", "Interpreter"]
LHS = RHS
OP = typing.Callable[[LHS, RHS], "ResolutionDefinition"]


class InvalidOrdering(Exception):
    """
    Raised when the given set of ordering pairs results in something
    impossible to resolve.

    Example
    -------
    ENV > ENV
    ENV > CFG > ENV

    etc.
    """

    pass


class ResolutionDefinition:
    """
    This class handles the definitions of resolution orderings. Its most
    dynamic behavior is overriding ``>`` and ``<`` operators. This allows
    developers to augment resolution orderings.

    Example
    -------
    >>> import configurables as conf
    >>>
    >>> @conf.configurables("Test", ordering=conf.ENV > conf.CFG)
    >>> @conf.param("key", type=str)
    >>> def load(key):
    >>>     print(key)

    This particular example would have ``configurables`` use values found
    in ENV (environmental variables) *above* values found in configuration
    files.

    Notes
    -----
    By default orderings are as follows CLI > CFG > ENV.
    """

    def __init__(self, first_element: "RHS"):
        self.interpreter_order = [first_element]

    def __lt__(self, rhs: "RHS"):
        if rhs in self.interpreter_order:
            raise InvalidOrdering()

        self.interpreter_order.insert(0, rhs)
        return self

    def __gt__(self, rhs: "RHS") -> "ResolutionDefinition":
        if rhs in self.interpreter_order:
            raise InvalidOrdering()

        self.interpreter_order.append(rhs)
        return self

    def __repr__(self):
        return " > ".join(map(str, self.interpreter_order))

    def load(self, **context: typing.Any) -> dict:
        payload = {}

        for interpreter in self.interpreter_order:
            kwargs = interpreter.load(**context)
            payload.update(kwargs)

        return payload


def autoparse_config(
    path: pathlib.Path, section: typing.Optional[str] = None
) -> dict:
    path = pathlib.Path(path).expanduser()
    global PARSING_REGISTRY
    func = PARSING_REGISTRY.get(path.suffix, PARSING_REGISTRY[".ini"])
    if section is None:
        return func(path)
    return func(path, section)


def register(*extensions: str) -> typing.Callable:
    def decoration(func):
        global PARSING_REGISTRY
        for extension in extensions:
            PARSING_REGISTRY[extension] = func
        return func

    return decoration


@register(".ini", ".conf")
def parse_ini(
    config_path: pathlib.Path, key: str
) -> configparser.SectionProxy:
    """Parse an ini file.
    Parameters
    ----------
    config_path: pathlib.Path
        The path to the desired ini configuration file
    key: str
        The section of the ini file to read in as keyword arguments
    """
    config = configparser.ConfigParser()
    expanded = config_path.expanduser()
    config.read(expanded)
    established_keys = config.sections()
    if key not in established_keys:
        established_keys = config.sections()
        content = open(expanded, "rt").read()
        raise KeyError(
            f"Could not find section '{key}', "
            f"only found [{', '.join(established_keys)}]."
            f"Config File: {config_path}\n"
            "---POTENTIALLY PRINTED SECRETS---\n"
            "Please review before copy-paste!\n"
            f"{content}"
            "---END CONFIG CONTENT---"
        )
    return config[key]


class Interpreter:
    name: typing.Optional[str] = None

    def load(self, **context: typing.Any) -> dict:
        return self.interpret(context)

    def interpret(self, context: dict) -> dict:
        raise NotImplementedError

    def _coalese(self, rhs: RHS, op: OP) -> ResolutionDefinition:
        if isinstance(rhs, ResolutionDefinition):
            lhs = self  # type: LHS
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

    def interpret(self, context: dict) -> dict:
        return dict(os.environ)


class Cli(Interpreter):
    name = "CLI"

    def interpret(self, context: dict) -> dict:
        args = sys.argv
        nargs = len(args)
        cursor = 1
        accumulator = {}  # type: dict[str, typing.Union[str, list[str], None]]
        while cursor < nargs:
            arg = args[cursor]
            if arg.startswith("--"):
                param_name = arg[2:]
                accumulator[param_name] = None

                cursor += 1
                while cursor < nargs and not args[cursor].startswith("--"):
                    arg = args[cursor]
                    current_val = accumulator[param_name]
                    if isinstance(current_val, str):
                        accumulator[param_name] = [current_val, arg]
                    elif isinstance(current_val, list):
                        current_val.append(arg)
                    elif current_val is None:
                        accumulator[param_name] = arg
                    cursor += 1
        return accumulator


class Cfg(Interpreter):
    name = "CFG"

    def interpret(self, context: dict) -> dict:
        try:
            config_path = context["config_path"]
        except KeyError:
            return {}

        result = autoparse_config(
            config_path, **context.get("parse_kwargs", {})
        )
        return result


ENV = Env()
CLI = Cli()
CFG = Cfg()
