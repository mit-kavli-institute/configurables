import configparser

from hypothesis import note
from hypothesis import strategies as st

from configurables import parse

RAW_TYPES = (str, int, float)

CONFIG_PARSE_CHAR_BLACKLIST = list("\\ %[]:;=\xa0#")

CONFIG_PARSE_ALPHABET = st.characters(
    blacklist_characters=CONFIG_PARSE_CHAR_BLACKLIST,
    blacklist_categories=["C", "Z"],
)


def write_ini_configuration(fout, header, configuration):
    config = configparser.ConfigParser()
    config[header] = configuration
    config.write(fout)
    fout.seek(0)
    note(fout.read())


def write_multi_ini_configuration(fout, configuration):
    config = configparser.ConfigParser()
    for header, subconfiguration in configuration.items():
        config[header] = subconfiguration
    config.write(fout)
    fout.seek(0)
    note(fout.read())


def write_env_configuration(monkeypatch, configuration):
    for key, value in configuration.items():
        monkeypatch.setenv(key, str(value))


def write_cli_configuration(monkeypatch, configuration):
    argv = ["fakecmd"]
    for key, value in configuration.items():
        argv.append(f"--{key.replace(' ', '-')}")
        argv.append(str(value))

    monkeypatch.setattr("sys.argv", argv)


def configurations():
    return st.dictionaries(
        st.text(min_size=1, alphabet=CONFIG_PARSE_ALPHABET).map(str.lower),
        st.one_of(
            st.text(alphabet=CONFIG_PARSE_ALPHABET, min_size=1),
            st.integers(),
            st.floats(),
        ),
        min_size=1,
    )


def multi_configurations():
    return st.dictionaries(
        st.text(min_size=1, alphabet=CONFIG_PARSE_ALPHABET),
        configurations(),
        min_size=1,
    )


@st.composite
def config_strings(draw):
    return draw(st.text(min_size=1, alphabet=CONFIG_PARSE_ALPHABET))


@st.composite
def resolutions(draw):
    bag = st.sampled_from([parse.ENV, parse.CLI, parse.CFG])

    return draw(st.lists(bag, min_size=1, unique=True))
