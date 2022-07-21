import pathlib
from multiprocessing import cpu_count
from tempfile import TemporaryDirectory

from hypothesis import given
from hypothesis import strategies as st

import configurables as conf
from configurables import configurable, define_param


@configurable("Credentials")
@define_param("username", type=str)
@define_param("password", type=str)
def login(username, password):
    return username, password


@conf.configurable("PipelineSettings")
@conf.define_param("ra", type=float)
@conf.define_param("dec", type=float)
@conf.define_option("n_workers", type=int, default=cpu_count())
@conf.define_option("output_path", type=pathlib.Path, default="./")
def run_pipeline(ra, dec, n_workers, output_path):
    return (
        f"RA: {ra}, DEC: {dec}\n"
        f"Will run with {n_workers} processes\n"
        f"Placing output to {output_path}"
    )


def test_login():
    with TemporaryDirectory() as tmpdir:
        configpath = pathlib.Path(tmpdir) / pathlib.Path("config.ini")
        with open(configpath, "wt") as fout:
            fout.write("[Credentials]\n")
            fout.write("username=username\n")
            fout.write("password=password\n")
        username, password = login(configpath)
        assert username == "username"
        assert password == "password"


@given(st.floats(), st.floats(), st.integers())
def test_run_pipeline_bare(ra, dec, n_workers):
    with TemporaryDirectory() as tmpdir:
        configpath = pathlib.Path(tmpdir) / pathlib.Path("config.ini")
        with open(configpath, "wt") as fout:
            fout.write("[PipelineSettings]\n")
            fout.write(f"ra={ra}\n")
            fout.write(f"dec={dec}\n")
            fout.write(f"n_workers={n_workers}\n")
            fout.write("output_path=./output\n")
        string = run_pipeline(configpath)
        point_str, worker_str, output = string.split("\n")
        assert str(ra) in point_str
        assert str(dec) in point_str
        assert str(n_workers) in worker_str
