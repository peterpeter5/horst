from os import path
import pytest
from ..horst import Horst
from ..python import _create_environment, CreateEnv, virtualenv, dependencies, _update_environment, UpdateEnv


here = path.dirname(__file__)


@pytest.fixture(autouse=True)
def delete_horst():
    horst = Horst("")
    horst._invalidate()


def test_create_environment_when_no_env_is_present():
    Horst(__file__)
    tasks = _create_environment({"name": ".env", "python": "python3"})
    assert len(tasks) == 1
    create_env_task = tasks[0]
    assert isinstance(create_env_task, CreateEnv)
    project_path = path.join(here, ".env")
    print(here)
    assert str(create_env_task) == "virtualenv -p python3 " + project_path


def test_create_environment_when_env_is_present_results_in_no_actions():
    import horst
    project_path = path.join(path.dirname(horst.__file__), "..", "anything.py")
    path_with_env = path.abspath(project_path)
    Horst(path_with_env)
    tasks = _create_environment({"name": ".env", "python": "doesn't matter"})
    assert tasks == []


def test_virtualenv():
    virtenv_config = virtualenv({".env": {"python": "/usr/bin/python"}})
    assert virtenv_config == {"name": ".env", "python": "/usr/bin/python"}


def test_virtualenv_default():
    virtenv_config = virtualenv()
    assert virtenv_config == {"name": ".env", "python": "python"}


def test_update_environment_returns_empty_when_no_dependencys():
    tasks = _update_environment({"install": [], "build": []}, {"name": ""})
    assert tasks == []


def test_update_environment_returns_pip_install_cmd_when_deps():
    Horst(__file__)
    pip_install = _update_environment(
        {"install": ["wheel"], "test": ["horst"]}, {"name": ".env"})
    expected_cmd = UpdateEnv(path.join(here, ".env"), ["wheel", "horst"])
    assert pip_install == [expected_cmd]


def test_update_env_cmd():
    pip_cmd = UpdateEnv("/path/to/env", ["dep1", "dep2", "dep3==2"])
    assert str(pip_cmd) == "/path/to/env/bin/pip install --upgrade dep1 dep2 dep3==2" 