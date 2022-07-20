#!/usr/bin/env python

"""Tests for `configurables` package."""
from tempfile import NamedTemporaryFile

from hypothesis import given

from configurables import configure

from . import strategies as c_st


def _uno_reverse(**kwargs):
    return kwargs


@given(c_st.config_strings(), c_st.configurations())
def test_loading_ini(header, configuration):
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
