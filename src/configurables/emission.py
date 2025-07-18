from __future__ import annotations

import configparser
import pathlib
import typing

EMISSION_REGISTRY: dict[
    str,
    typing.Callable[
        [pathlib.Path, str, dict[typing.Any, typing.Any]], pathlib.Path
    ],
] = {}


def autoemit_config(
    path: pathlib.Path,
    configuration: dict[typing.Any, typing.Any],
    section: typing.Optional[str] = None,
) -> pathlib.Path:
    func = EMISSION_REGISTRY[path.suffix]
    if section is None:
        section = "DEFAULT"
    return func(path, section, configuration)


def register(
    *extensions: str
) -> typing.Callable[[typing.Callable], typing.Callable]:
    def decoration(func: typing.Callable) -> typing.Callable:
        for extension in extensions:
            EMISSION_REGISTRY[extension] = func
        return func

    return decoration


@register(".ini", ".conf")
def emit_init(
    config_path: pathlib.Path,
    header: str,
    configuration: dict[typing.Any, typing.Any],
) -> pathlib.Path:
    parser = configparser.ConfigParser()
    parser[header] = configuration

    real_path = config_path.expanduser().resolve()
    with open(real_path, "wt") as fout:
        parser.write(fout)

    return real_path
