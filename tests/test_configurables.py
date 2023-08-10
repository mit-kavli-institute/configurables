#!/usr/bin/env python

"""Tests for `configurables` package."""
import pathlib
from tempfile import NamedTemporaryFile, TemporaryDirectory

from hypothesis import given

from configurables import configure

from . import strategies as c_st


def _uno_reverse(**kwargs):
    return kwargs


@given(c_st.config_strings(), c_st.configurations())
def test_loading_ini_override(header, configuration):
    with NamedTemporaryFile("w+t") as tmpfile:
        c_st.write_ini_configuration(tmpfile, header, configuration)
        tmpfile.seek(0)
        result = configure(
            _uno_reverse,
            tmpfile.name,
            config_group=header,
            extension_override=".ini",
        )
        assert set(result.keys()) == set(configuration.keys())

        for key, value in result.items():
            assert value == str(configuration[key])


@given(c_st.config_strings(), c_st.configurations())
def test_loading_ini(header, configuration):
    with TemporaryDirectory() as folder:
        tmpfile = pathlib.Path(folder) / "config.ini"
        with open(tmpfile, "w+t") as fout:
            c_st.write_ini_configuration(fout, header, configuration)
        result = configure(_uno_reverse, tmpfile, config_group=header)
        assert set(result.keys()) == set(configuration.keys())

        for key, value in result.items():
            assert value == str(configuration[key])
