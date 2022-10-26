import pathlib
from tempfile import TemporaryDirectory

from configurables import configurable, param


@configurable("Credentials")
@param("username", type=str)
@param("password", type=str)
def login(username, password):
    return username, password


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
