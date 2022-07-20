import configparser
import pathlib

import deal

PARSING_REGISTRY = {}


def autoparse_config(path: pathlib.Path, group) -> dict:
    global PARSING_REGISTRY
    func = PARSING_REGISTRY[path.suffix]
    return func(path)


def register(extension):
    def decoration(func):
        global PARSING_REGISTRY
        PARSING_REGISTRY[extension] = func
        return func

    return decoration


@deal.raises(KeyError)
@deal.pre(lambda _: _.config_path.exists())
@deal.pre(lambda _: isinstance(_.config_path, pathlib.Path))
@deal.pure
@register(".ini")
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
