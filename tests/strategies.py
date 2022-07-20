import configparser

from hypothesis import strategies as st

RAW_TYPES = (str, int, float)

CONFIG_PARSE_CHAR_BLACKLIST = list(" %[]:;=\xa0#")

CONFIG_PARSE_ALPHABET = st.characters(
    blacklist_characters=CONFIG_PARSE_CHAR_BLACKLIST,
    blacklist_categories=["C"],
)


def write_ini_configuration(fout, header, configuration):
    config = configparser.ConfigParser()
    config[header] = configuration
    config.write(fout)


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


@st.composite
def config_strings(draw):
    return draw(st.text(min_size=1, alphabet=CONFIG_PARSE_ALPHABET))
