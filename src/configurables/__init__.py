"""Top-level package for Configurables."""
from configurables.configurable import configurable, configure, option, param
from configurables.parse import CFG, CLI, ENV
from configurables._version import __version__

__author__ = """William Christopher Fong"""
__email__ = "willfong@mit.edu"


__all__ = [
    "configure",
    "param",
    "option",
    "configurable",
    "ENV",
    "CFG",
    "CLI",
]
