import pytest
from os import path

from horst import Horst
from horst.build import from_git_config, _render_setuppy, _create_setup, _update_setup, _clean_install_fragments, \
    _run_bdist_wheel
from horst.effects import CreateFile, UpdateFile, DeleteFileOrFolder, RunCommand


@pytest.fixture()
def horst():
    build_py = path.abspath(path.join(path.dirname(__file__), "..", "..", "build.py"))
    horst = Horst("")
    horst._invalidate()
    horst = Horst(build_py)
    horst.configure()
    yield horst
    horst._invalidate()


@pytest.fixture()
def setup_config():
    return dict(
        name="horst",
        version="1",
        description="short",
        long_description="long",
        url="/url/to",
        packages=[],
        install_requires=[""]
    )


def test_from_git_with_existing_value(horst):
    config = from_git_config("bare")
    assert config == {"bare": "false"}


def test_from_git_not_existing_value(horst):
    config = from_git_config("not-existing-key")
    assert config == {}


def test_format_setup_py_template(setup_config):
    rendred_setuppy = _render_setuppy(setup_config)
    expected_text = """# THIS IS AN AUTOGENERATED FILE! DO NOT EDIT HERE DIRECTLY! USE build.py fot this

from setuptools import setup, find_packages

setup(
    name="horst",
    version="1",
    description="short",
    long_description="long",
    url="/url/to",
"""
    assert rendred_setuppy.startswith(expected_text)


def test_create_setuppy():
    create_file = _create_setup("/not/exitsting/path")
    assert create_file == [CreateFile("/not/exitsting/path", "")]

    no_file_create = _create_setup(__file__)
    assert no_file_create == []


def test_update_setuppy(setup_config):
    update_setup = _update_setup("/not/my/path", setup_config)
    assert isinstance(update_setup, list)
    assert len(update_setup) == 1
    assert isinstance(update_setup[0], UpdateFile)


def test_clean_install_fragments(horst):
    delete_folders = _clean_install_fragments()
    base = horst.project_path
    expected_folders = [path.join(base, "build"), path.join(base, "horst.egg-info")]
    assert delete_folders == [DeleteFileOrFolder(name) for name in expected_folders]


def test_bdist_wheel_cmd_without_clean(horst):
    cmds = _run_bdist_wheel(clean_intermediates=False)
    assert cmds == [RunCommand("python", ["setup.py", "bdist_wheel"])]


def test_bdist_wheel_with_cleanup(horst):
    cmds = _run_bdist_wheel(clean_intermediates=True)
    assert len(cmds) > 1
    assert isinstance(cmds[-1], DeleteFileOrFolder)

