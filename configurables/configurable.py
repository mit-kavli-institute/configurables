import os
import pathlib
import typing

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
