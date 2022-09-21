"""Top-level package for Configurables."""
from configurables.configurable import (
    configurable,
    configure,
    define_option,
    define_param,
)
from configurables.parse import CFG, CLI, ENV

__author__ = """William Christopher Fong"""
__email__ = "willfong@mit.edu"
__version__ = "0.1.0"


__all__ = [
    "configure",
    "define_param",
    "define_option",
    "configurable",
    "ENV",
    "CFG",
    "CLI",
]
