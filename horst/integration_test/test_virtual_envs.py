from .horst_projects import horst_project, get_output_checked, minimal_horst, horst_with_dependencies, \
    get_command_section
from click.testing import CliRunner
import pytest
from ..__main__ import cli
from os import path
from contextlib import contextmanager
import re
import subprocess


@contextmanager
def no_virtaul_env_present(runner):
    with runner.isolated_filesystem() as folder, horst_project(minimal_horst, folder) as build_file:
        yield build_file


@pytest.fixture()
def runner():
    return CliRunner()


def test_when_no_env_existing_create_env_task_is_offered(runner):
    with no_virtaul_env_present(runner) as build_file:
        result = runner.invoke(cli(build_file))
        cmd_overview = get_command_section(get_output_checked(result))
        assert "env:create" in cmd_overview


def test_even_though_no_env_existing_update_env_is_offered(runner):
    with no_virtaul_env_present(runner) as build_file:
        result = runner.invoke(cli(build_file))
        cmd_overview = get_command_section(get_output_checked(result))
        assert "env:update" in cmd_overview


def test_dry_run_env_create_shows_virtualenv_cmd(runner):
    with no_virtaul_env_present(runner) as build_file:
        result = runner.invoke(cli(build_file), ["-d", "env:create"])
        output = get_output_checked(result)
        assert "virtualenv" in output


def test_dry_run_env_update_shows_pip_install_cmd(runner):
    with runner.isolated_filesystem() as folder, horst_project(horst_with_dependencies, folder) as build_file:
        result = runner.invoke(cli(build_file), ["-d", "env:update"])
        output = get_output_checked(result)
        assert "pip install" in output


@pytest.mark.slow
def test_run_env_create_works_like_expected(runner):
    with no_virtaul_env_present(runner) as build_file:
        result = runner.invoke(cli(build_file), ["env:create"])
        output = get_output_checked(result)
        last_line = list(filter(lambda line: line.startswith("\t|-->"), output.splitlines()))[-1]

        assert "OK" in last_line


@pytest.mark.slow
def test_run_env_update_will_create_an_environment_before_installing_deps(runner):
    with runner.isolated_filesystem() as folder, horst_project(horst_with_dependencies, folder) as build_file:
        result = runner.invoke(cli(build_file), ['-v', "env:update"])
        output = get_output_checked(result)
        num_oks = len(re.findall("OK", output))
        assert num_oks == 2
        env_base_path = path.join(path.dirname(build_file), ".env")
        assert path.exists(env_base_path)
        result = subprocess.run("./.env/bin/python ./file_with_dependency.py", cwd=path.dirname(build_file), shell=True)
        assert 0 == result.returncode
