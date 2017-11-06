from click.testing import CliRunner
import pytest
from ..__main__ import cli
from os import path


@pytest.fixture()
def runner():
    return CliRunner()


def create_minimal_horst_project(folder):
    with open(path.join(folder, "build.py"), "w") as file:
        file.write("""
from horst import *
Horst(__file__)

dependencies(environment=virtualenv())

""")



def test_horst_no_build_py_exists_has_std_tasks_as_commands(runner):
    with runner.isolated_filesystem():
        result = runner.invoke(cli(""))
        assert result.exit_code == 0
        cmd_ouput = result.output.split("Commands:")[-1]
        assert "debug" in cmd_ouput      


def test_horst_with_minimal_build_py(runner):
    with runner.isolated_filesystem() as folder:
        create_minimal_horst_project(folder)
        result = runner.invoke(cli(path.join(folder, "build.py")))
        assert result.exit_code == 0
        cmd_ouput = result.output.split("Commands:")[-1]
        assert "env" in cmd_ouput


def test_horst_debug_tasks_can_be_executed_even_in_empty_dir(runner):
    with runner.isolated_filesystem() as folder:
        result = runner.invoke(cli(path.join(folder, "build.py")), ["debug"])
        assert result.exit_code == 0
        

