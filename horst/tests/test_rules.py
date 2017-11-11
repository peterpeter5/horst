from ..rules import Engine, _Stage, env, create, update, depends_on_stage, finalize_stage
import pytest


class A(_Stage):
    pass


class B(_Stage):
    pass


class C(_Stage):
    pass


rules = Engine()
_ab_stage = A() / B()
_first_stack_stage = A() / B()
_second_stack_stage = C()


@rules.config(A(""))
def config_smthng(a, b):
    return [a, b], None


@rules.register(_ab_stage)
def put_tasks_on_b():
    return ["b"]


@rules.register(_first_stack_stage)
@rules.register(_second_stack_stage)
def put_tasks_stacked():
    return ["stacked"]


@rules.register(_ab_stage, route="a/c/a/b")
def tasks_with_custom_route():
    pass


def test_config_function_reslut_is_saved_in_engine():
    config_smthng("a", 2)
    assert rules._config == {'config_smthng': ['a', 2]}


def test_stage_div_protocol_with_wrong_types():
    with pytest.raises(TypeError):
        7 / A()


def test_stage_div_protocol_and_string_serialization():
    assert str(A() / B() / B() / A()) == "A:B:B:A"


def test_preconfigured_stages_with_names_protocol():
    assert str(env / create / update) == "env:create:update"


def test_stage_has_name():
    stage_with_class_name = A()
    stage_with_custom_name = _Stage("custom")
    assert stage_with_class_name.name == "A"
    assert stage_with_custom_name.name == "custom"


def test_stages_and_routes_can_register_tasks():
    a = A()
    a.register_tasks(["a"])
    assert a.tasks == ("a",)

    ab = a / B()
    ab.register_tasks(["a", "b"])
    ab_chain = list(ab)
    assert ab_chain[0].tasks == ("a",)
    assert ab_chain[1].tasks == ("a", "b")


def test_stages_give_a_tasks_chain_when_asked():
    a = A()
    a.register_tasks(["a"])

    ab = a / B()
    ab.register_tasks((["a"], ["b"]))
    assert ab.tasks == [
        ("a",),
        (["a"], ["b"])
    ]


def test_stages_and_routes_can_have_a_transformation_function():
    a = A()
    a.register_tasks([1])
    a.task_transformer(lambda x: x + 1)
    assert a.tasks == (2,)

    ab = A().register_tasks(["a"]) / B().register_tasks(["CA"])
    ab.task_transformer(lambda x: x.upper())
    assert ab.tasks == [("A",), ("CA",)]


def test_rules_register_decorator_puts_config_results_on_stage():
    put_tasks_on_b()
    expected_tasks = [(), ("b",)]
    assert _ab_stage.tasks == expected_tasks
    assert rules._stages == {"A:B": _ab_stage}


@pytest.mark.xfail
def test_rules_stage_routes_can_be_stacked():
    put_tasks_stacked()
    expected_tasks = ["stacked"]
    assert _first_stack_stage.tasks == [[], expected_tasks]
    assert _second_stack_stage == expected_tasks
    assert rules._stages == {
        "A.B": [[], expected_tasks],
        "C": expected_tasks
    }


def test_register_can_have_custom_routes():
    tasks_with_custom_route()
    actual_stages = list(rules.get_stages().keys())
    assert "a:c:a:b" in actual_stages


def test_registered_task_lists_are_immutable():
    tasks_list = "asdf"
    tasks = rules.register(_Stage("a"))(lambda y: y)(tasks_list)
    assert id(tasks) != id(tasks_list)


def test_stage_tasks_are_immutable_for_debugging_but_act_mutable():
    stage = _Stage("u")
    stage.register_tasks(["asdf"])
    stage.register_tasks(["new task"])
    assert stage._tasks == [("asdf",), ("new task",)]
    assert stage.tasks == ("new task",)


def test_depends_on():
    put_tasks_on_b()
    tasks_with_custom_route()
    assert str(A() / B()) == str(depends_on_stage(rules, ["A:B"])())
    assert str(_ab_stage) == str(depends_on_stage(rules, ["a:c:a:b"])())
    assert str(A() / B()) == str(depends_on_stage(rules, ["A:B", "a:c:a:b"])())


def test_finalize_stage():
    stage_a = A()
    stage_a.register_depends_on(C())
    route = stage_a / B()
    assert str(finalize_stage(route)) == str(C() / A() / B())
