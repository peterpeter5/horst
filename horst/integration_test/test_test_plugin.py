import os

from .horst_pojects import get_output_checked, isolated_horst_project, horst_with_no_tests, \
    get_stage_result_from_output, get_command_section, horst_with_tests_that_pass, horst_with_test_that_fail
from click.testing import CliRunner
from ..__main__ import cli
import pytest


@pytest.fixture()
def runner():
    return CliRunner()


def test_horst_project_with_test_plugin_but_no_test_returns_up_to_date(runner):
    with isolated_horst_project(horst_with_no_tests, runner) as build_file:
        result = runner.invoke(cli(build_file), ["test"])
        stage_results = get_stage_result_from_output(get_output_checked(result))
        assert stage_results == [("test", "UP-TO-DATE"), ("test:unittest", "UP-TO-DATE")]


def test_horst_overview_contains_test_command(runner):
    with isolated_horst_project(horst_with_no_tests, runner) as build_file:
        result = runner.invoke(cli(build_file))
        commands = get_command_section(get_output_checked(result))
        assert "test" in commands


def test_dry_run_with_tests(runner):
    with isolated_horst_project(horst_with_no_tests, runner) as build_file:
        result = runner.invoke(cli(build_file), ['-d', 'test'])
        lines = get_output_checked(result).splitlines()
        dirname = os.path.dirname(build_file)
        assert "pytest --color=yes unit" in lines[-1]


def test_run_tests_that_pass(runner):
    with isolated_horst_project(horst_with_tests_that_pass, runner) as build_file:
        result = runner.invoke(cli(build_file), ['test'])
        stage_results = get_stage_result_from_output(get_output_checked(result))
        assert stage_results == [("test", "UP-TO-DATE"), ("test:unittest", "OK")]


def test_run_tests_that_fail(runner):
    with isolated_horst_project(horst_with_test_that_fail, runner) as build_file:
        result = runner.invoke(cli(build_file), ['test'])
        assert result.exit_code != 0
        stage_results = get_stage_result_from_output(result.output)
        assert stage_results == [("test", "UP-TO-DATE"), ("test:unittest", "ERROR")]

