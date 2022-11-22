import pathlib
from math import isnan
from tempfile import TemporaryDirectory

from hypothesis import given

from configurables import configurable, param

from . import strategies as c_st


def _reflector(**kwargs):
    return kwargs


@given(c_st.config_strings(), c_st.configurations())
def test_emission_equilvancy(header, configuration):
    with TemporaryDirectory() as folder:
        filepath = pathlib.Path(folder) / "config.ini"
        emit_path = pathlib.Path(folder) / "emitted.ini"
        with open(filepath, "w+") as fout:
            c_st.write_ini_configuration(fout, header, configuration)

        f = _reflector
        for key, value in configuration.items():
            if type(value) == str:
                f = param(key)(f)
            else:
                f = param(key, type=type(value))(f)
        f = configurable(header)(f)

        test_path = f.emit(emit_path, filepath)

        result = f(test_path)
        for key, value in result.items():
            if isinstance(value, float) and isnan(value):
                assert isnan(configuration[key])
            else:
                assert value == configuration[key]
