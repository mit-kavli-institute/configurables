import pathlib
from tempfile import TemporaryDirectory

import pytest
from hypothesis import given
from hypothesis import strategies as st

from configurables import configurable, param, parse

from . import strategies as c_st


def _reflector(**kwargs):
    return kwargs


@given(c_st.multi_configurations(), st.data())
def test_missing_key_error_raised(configuration, data):
    target_header = data.draw(st.sampled_from(sorted(configuration.keys())))
    missing_key = data.draw(
        st.sampled_from(sorted(configuration[target_header].keys()))
    )
    reference_configuration = configuration[target_header]
    reference_configuration.pop(missing_key)
    with TemporaryDirectory() as folder:
        filepath = pathlib.Path(folder) / "config.ini"
        with open(filepath, "w+t") as fout:
            c_st.write_multi_ini_configuration(fout, configuration)

        f = param(missing_key)(_reflector)
        f = configurable(target_header)(f)
        with pytest.raises(KeyError):
            f(filepath)


def test_against_empty_schema():
    with pytest.raises(ValueError):
        _ = configurable("whatever")(_reflector)


@given(st.sampled_from([parse.ENV, parse.CLI, parse.CFG]))
def test_against_logically_unsound_order(order):
    with pytest.raises(parse.InvalidOrdering):
        _ = order > order
    with pytest.raises(parse.InvalidOrdering):
        _ = order < order
