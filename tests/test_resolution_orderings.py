import pathlib
from functools import reduce
from math import isnan
from tempfile import TemporaryDirectory

from hypothesis import HealthCheck, given, note, settings
from hypothesis import strategies as st

from configurables import configurable, param

from . import strategies as c_st


def _reflector(**kwargs):
    return kwargs


@settings(
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    max_examples=500,
)
@given(c_st.resolutions(), c_st.config_strings(), st.data())
def test_orderings(monkeypatch, ordering, header, data):
    configurations = data.draw(
        st.lists(
            c_st.configurations(),
            min_size=len(ordering),
            max_size=len(ordering),
        )
    )
    with TemporaryDirectory() as folder, monkeypatch.context() as m:
        filepath = pathlib.Path(folder) / "config.ini"
        reference = {}
        types = {}
        defined_keys = set()
        for order, conf in zip(ordering, configurations):
            reference.update(conf)
            if order.name == "ENV":
                c_st.write_env_configuration(m, conf)
            elif order.name == "CLI":
                c_st.write_cli_configuration(m, conf)
            elif order.name == "CFG":
                with open(filepath, "w+") as fout:
                    c_st.write_ini_configuration(fout, header, conf)
            defined_keys.update(conf.keys())
            for key, value in conf.items():
                types[key] = type(value)

        order = reduce(lambda lhs, rhs: lhs > rhs, ordering)

        func = _reflector
        for key in defined_keys:
            type_ = types[key]
            func = param(key, type=type_)(func)
        func = configurable(header, order=order)(func)

        if any(order.name == "CFG" for order in ordering):
            result = func(filepath)
        else:
            result = func()

        order_debug = [order.name for order in ordering]
        note(f"Order: {' > '.join(order_debug)}")
        note(func)
        for key, value in result.items():
            ref = reference[key]
            if isinstance(value, float) and isnan(value):
                assert isnan(ref)
            else:
                assert value == ref


@settings(
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    max_examples=500,
)
@given(c_st.resolutions(), c_st.config_strings(), st.data())
def test_orderings_lt(monkeypatch, ordering, header, data):
    configurations = data.draw(
        st.lists(
            c_st.configurations(),
            min_size=len(ordering),
            max_size=len(ordering),
        )
    )
    with TemporaryDirectory() as folder, monkeypatch.context() as m:
        filepath = pathlib.Path(folder) / "config.ini"
        reference = {}
        types = {}
        defined_keys = set()
        for order, conf in zip(ordering[::-1], configurations):
            reference.update(conf)
            if order.name == "ENV":
                c_st.write_env_configuration(m, conf)
            elif order.name == "CLI":
                c_st.write_cli_configuration(m, conf)
            elif order.name == "CFG":
                with open(filepath, "w+") as fout:
                    c_st.write_ini_configuration(fout, header, conf)
            defined_keys.update(conf.keys())
            for key, value in conf.items():
                types[key] = type(value)

        order = reduce(lambda lhs, rhs: lhs < rhs, ordering)

        func = _reflector
        for key in defined_keys:
            type_ = types[key]
            func = param(key, type=type_)(func)
        func = configurable(header, order=order)(func)

        if any(order.name == "CFG" for order in ordering):
            result = func(filepath)
        else:
            result = func()

        order_debug = [order.name for order in ordering]
        note(f"Order: {' < '.join(order_debug)}")
        note(func)
        for key, value in result.items():
            ref = reference[key]
            if isinstance(value, float) and isnan(value):
                assert isnan(ref)
            else:
                assert value == ref
