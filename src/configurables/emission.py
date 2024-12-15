import configparser
import pathlib
import typing

EMISSION_REGISTRY = {}  # type: typing.Dict[str, typing.Any]


def autoemit_config(
    path: pathlib.Path,
    configuration: typing.Dict[typing.Any, typing.Any],
    section: typing.Optional[str] = None,
) -> dict:
    global EMISSION_REGISTRY
    func = EMISSION_REGISTRY[path.suffix]
    return func(path, section, configuration)


def register(*extensions: str) -> typing.Callable:
    def decoration(func):
        global EMISSION_REGISTRY
        for extension in extensions:
            EMISSION_REGISTRY[extension] = func
            return func

    return decoration


@register(".ini", ".conf")
def emit_init(
    config_path: pathlib.Path,
    header: str,
    configuration: typing.Dict[typing.Any, typing.Any],
) -> pathlib.Path:
    parser = configparser.ConfigParser()
    parser[header] = configuration

    real_path = config_path.expanduser().resolve()
    with open(real_path, "wt") as fout:
        parser.write(fout)

    return real_path
