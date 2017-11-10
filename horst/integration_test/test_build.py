import pytest
from click.testing import CliRunner
from .horst_projects import isolated_horst_project, minimal_horst, get_command_section, get_output_checked, \
    get_stage_results
from ..__main__ import cli


UTD = "UP-TO-DATE"

@pytest.fixture()
def runner():
    return CliRunner()


def test_horst_can_build_wheel_cmd_is_in_overview(runner):
    with isolated_horst_project(minimal_horst, runner) as build_file:
        result = runner.invoke(cli(build_file), [])
        commands = get_command_section(get_output_checked(result))
        assert "build:wheel" in commands


def test_horst_can_build_eventhough_no_setup_is_available(runner):
    with isolated_horst_project(minimal_horst, runner) as build_file:
        result = runner.invoke(cli(build_file), ["build:wheel"])
        stage_results = get_stage_results(get_output_checked(result))
        expected_results = [
            ("build", UTD),
            ("build:create_setup", "OK"),
            ("build:create_setup:update_setup", "OK"),
            ("build:create_setup:update_setup:build_wheel", ["OK", "OK", "OK"])
        ]
        assert stage_results == expected_results