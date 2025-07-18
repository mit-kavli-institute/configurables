import pathlib
from math import isnan
from tempfile import NamedTemporaryFile, TemporaryDirectory

from hypothesis import given, note
from hypothesis import strategies as st

from configurables import configurable, configure, option, param
from configurables.core import ConfigurationBuilder

from . import strategies as c_st


def _reflector(**kwargs):
    return kwargs


def test_add_parameter_construction():
    f = param("test_key", type=str)(_reflector)
    assert isinstance(f, ConfigurationBuilder)


@given(c_st.config_strings(), c_st.configurations())
def test_building_configurable(header, configuration):
    with TemporaryDirectory() as folder:
        filepath = pathlib.Path(folder) / pathlib.Path("config.ini")
        note(filepath)
        with open(filepath, "w+") as fout:
            c_st.write_ini_configuration(fout, header, configuration)

        f = _reflector
        for key, value in configuration.items():
            if isinstance(value, str):
                f = param(key)(f)
            else:
                f = param(key, type=type(value))(f)
        f = configurable(header)(f)
        result = f(filepath)
        for key, value in result.items():
            if isinstance(value, float) and isnan(value):
                assert isnan(configuration[key])
            else:
                assert value == configuration[key]


@given(c_st.config_strings(), c_st.configurations(), st.data())
def test_building_configurable_options(header, configuration, data):
    missing_param = data.draw(st.sampled_from(sorted(configuration.keys())))
    ref_value = configuration.pop(missing_param)
    with TemporaryDirectory() as folder:
        filepath = pathlib.Path(folder) / pathlib.Path("config.ini")
        note(str(filepath))
        with open(filepath, "w+") as fout:
            c_st.write_ini_configuration(fout, header, configuration)

        f = _reflector
        for key, value in configuration.items():
            if isinstance(value, str):
                f = option(key, default=value)(f)
            else:
                f = option(key, type=type(value), default=value)(f)
        f = option(missing_param, type=type(ref_value), default=ref_value)(f)
        f = configurable(header)(f)
        result = f(filepath)

        configuration[missing_param] = ref_value
        for key, value in result.items():
            if isinstance(value, float) and isnan(value):
                assert isnan(configuration[key])
            else:
                assert value == configuration[key]


@given(c_st.config_strings(), c_st.configurations())
def test_partial(header, configuration):
    with TemporaryDirectory() as folder:
        filepath = pathlib.Path(folder) / "config.ini"
        note(str(filepath))
        with open(filepath, "w+") as fout:
            c_st.write_ini_configuration(fout, header, configuration)

        f = _reflector
        for key, value in configuration.items():
            if isinstance(value, str):
                f = param(key)(f)
            else:
                f = param(key, type=type(value))(f)
        f = configurable(header)(f)
        partial = f.partial(filepath)
        result = partial()
        for key, value in result.items():
            if isinstance(value, float) and isnan(value):
                assert isnan(configuration[key])
            else:
                assert value == configuration[key]


@given(st.data(), c_st.config_strings(), c_st.configurations())
def test_overrides(data, header, configuration):
    override_keys = st.text(min_size=1).filter(
        lambda s: s not in configuration
    )
    override_values = data.draw(
        st.dictionaries(
            override_keys,
            st.one_of(st.none(), st.integers(), st.floats(), st.text()),
        )
    )
    with TemporaryDirectory() as folder:
        filepath = pathlib.Path(folder) / pathlib.Path("config.ini")
        with open(filepath, "w+") as fout:
            c_st.write_ini_configuration(fout, header, configuration)

        f = _reflector
        for key, value in configuration.items():
            if isinstance(value, str):
                f = param(key)(f)
            else:
                f = param(key, type=type(value))(f)
        f = configurable(header)(f)
        result = f(filepath, **override_values)
        note(str(result))
        note(str(configuration))
        note(str(override_values))
        for key, value in result.items():
            note(key)
            try:
                ref = override_values[key]
            except KeyError:
                ref = configuration[key]
            if isinstance(value, float) and isnan(value):
                assert isnan(ref)
            else:
                assert value == ref


@given(c_st.multi_configurations(), st.data())
def test_group_override(configuration, data):
    target_header = data.draw(st.sampled_from(sorted(configuration.keys())))
    other_header = data.draw(st.sampled_from(sorted(configuration.keys())))
    reference_configuration = configuration[target_header]
    with TemporaryDirectory() as folder:
        filepath = pathlib.Path(folder) / "config.ini"
        with open(filepath, "w+") as fout:
            c_st.write_multi_ini_configuration(fout, configuration)
        f = _reflector
        for k, v in reference_configuration.items():
            if isinstance(v, str):
                f = param(k)(f)
            else:
                f = param(k, type=type(v))(f)
        f = configurable(other_header)(f)
        result = f(filepath, _section=target_header)
        for k, v in result.items():
            ref_value = reference_configuration[k]
            if isinstance(ref_value, float) and isnan(ref_value):
                assert isnan(v)
            else:
                assert v == ref_value


@given(st.data(), c_st.config_strings(), c_st.configurations())
def test_pass_through(data, header, configuration):
    f = _reflector
    complete_override = {}
    for key in configuration.keys():
        complete_override[key] = data.draw(
            st.one_of(st.none(), st.integers(), st.floats(), st.text())
        )

    for key, value in configuration.items():
        if isinstance(value, str):
            f = param(key)(f)
        else:
            f = param(key, type=type(value))(f)
    f = configurable(header)(f)

    result = f(**complete_override)
    for key, value in result.items():
        ref_value = complete_override[key]

        if isinstance(value, float) and isnan(value):
            assert isnan(ref_value)
        else:
            assert value == ref_value


@given(c_st.multi_configurations(), st.data())
def test_configuration_override(configuration, data):
    target_header = data.draw(st.sampled_from(sorted(configuration.keys())))
    reference_configuration = configuration[target_header]

    with NamedTemporaryFile("w+t") as tmpfile:
        c_st.write_multi_ini_configuration(tmpfile, configuration)
        result = configure(
            _reflector,
            tmpfile.name,
            config_group=target_header,
            extension_override=".ini",
        )
    assert set(result.keys()) == set(reference_configuration.keys())

    for k, v in result.items():
        assert v == str(reference_configuration[k])
