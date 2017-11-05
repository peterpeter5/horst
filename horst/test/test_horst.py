import pytest
from ..horst import Horst, get_project_path
from ..rules import Engine, _Stage
from os import path

a = _Stage("a")
b = _Stage("b")
a__b = a / b

rule = Engine()

@rule.register(a__b, route="b")
def b_conf():
    pass

@pytest.fixture(autouse=True)
def delete_horst():
    print("delete horst got called")
    horst = Horst("")
    horst._invalidate()


def test_horst_is_a_singleton():
    horst = Horst("")
    second_horst = Horst("asdf")
    assert horst == second_horst


def test_horst_is_a_singleton_but_can_be_killed_or_invalidated():
    first_horst = Horst("")
    first_horst._invalidate()
    second_horst = Horst("asdf")
    assert first_horst is not second_horst


def test_get_project_path_returns_dir_name_of_horst_instance():
    horst = Horst(__file__)
    assert get_project_path() == path.dirname(__file__) 


def test_get_project_path_results_in_empty_str_when_no_path_like_is_provided():
    Horst("asdf")
    assert "" == get_project_path() == path.dirname("asdf")


def test_get_project_path_is_coupled_to_horst_cycle():
    horse = Horst("asdf/file.py")
    assert "asdf" == get_project_path()

    horse._invalidate()
    new_horst = Horst("1/2/3")
    assert "1/2" == get_project_path() == new_horst.project_path 


def test_horst_get_commands_returns_cmd_path_and_stage_not_tasks():
    b_conf()
    horst = Horst("", rule)
    commands = horst.get_commands()
    assert commands == {"b": a__b}