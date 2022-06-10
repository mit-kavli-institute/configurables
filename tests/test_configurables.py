#!/usr/bin/env python

"""Tests for `configurables` package."""
import configparser
from tempfile import NamedTemporaryFile

from hypothesis import given, note
from hypothesis import strategies as st

from configurables import configure

CONFIG_PARSE_CHAR_BLACKLIST = list(" %[]:;=\xa0#")

CONFIG_PARSE_ALPHABET = st.characters(
    blacklist_characters=CONFIG_PARSE_CHAR_BLACKLIST,
    blacklist_categories=["C"],
)


def _write_ini_configuration(fout, header, configuration):
    config = configparser.ConfigParser()
    config[header] = configuration
    config.write(fout)


def _uno_reverse(**kwargs):
    return kwargs


@st.composite
def configurations(draw):
    return draw(
        st.dictionaries(
            st.text(min_size=1, alphabet=CONFIG_PARSE_ALPHABET).map(str.lower),
            st.one_of(
                st.text(alphabet=CONFIG_PARSE_ALPHABET, min_size=1),
                st.integers(),
                st.floats(),
            ),
            min_size=1,
        )
    )


@given(st.text(min_size=1, alphabet=CONFIG_PARSE_ALPHABET), configurations())
def test_loading_ini(header, configuration):
    with NamedTemporaryFile("w+t") as tmpfile:
        _write_ini_configuration(tmpfile, header, configuration)
        tmpfile.seek(0)
        tmpfile.seek(0)
        result = configure(
            _uno_reverse,
            tmpfile.name,
            config_group=header,
            extension_override=".ini",
        )
        assert set(result.keys()) == set(configuration.keys())

        note(result)
        for key, value in result.items():
            assert value == str(configuration[key])
