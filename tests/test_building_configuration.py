import pathlib
from math import isnan
from tempfile import TemporaryDirectory

from hypothesis import given, note

from configurables import configurable, define_param
from configurables.core import ConfigurationBuilder

from . import strategies as c_st


def _reflector(**kwargs):
    return kwargs


def test_add_parameter_construction():
    f = define_param("test_key", type=str)(_reflector)
    assert isinstance(f, ConfigurationBuilder)


@given(c_st.config_strings(), c_st.configurations())
def test_building_configurable(header, configuration):
    with TemporaryDirectory() as folder:
        filepath = pathlib.Path(folder) / pathlib.Path("config.ini")
        note(filepath)
        with open(filepath, "w") as fout:
            c_st.write_ini_configuration(fout, header, configuration)

        f = _reflector
        for key, value in configuration.items():
            f = define_param(key, type=type(value))(f)
        f = configurable(header)(f)
        result = f(filepath)
        for key, value in result.items():
            if isinstance(value, float) and isnan(value):
                assert isnan(configuration[key])
            else:
                assert value == configuration[key]