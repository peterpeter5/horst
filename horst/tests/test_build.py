import pytest
from os import path

from horst import Horst
from horst.build import from_git_config


@pytest.fixture()
def horst():
    build_py = path.abspath(path.join(path.dirname(__file__), "..", "..", "build.py"))
    horst = Horst("")
    horst._invalidate()
    yield Horst(build_py)
    horst._invalidate()


def test_from_git_with_existing_value(horst):
    config = from_git_config("bare")
    assert config == {"bare": "false"}


def test_from_git_not_existing_value(horst):
    config = from_git_config("not-existing-key")
    assert config == {}
