from ..rules import Engine, _Stage, env, create, update, depends_on_stage, finalize_stage, _RouteChain, \
    get_config_from_stage
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


@rules.config(A("conf"))
def config_smthng(a=0, b=0):
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
    assert rules._config == {'conf': ['a', 2]}


def test_config_function_is_saved_in_engine_as_func_when_not_called():
    def a_func():
        return 1

    rules.config(B("hello"))(a_func)
    assert rules._config["hello"].__name__ == a_func.__name__


def test_get_config_from_stage():
    @rules.config(B("cello"))
    def a_func(a=0):
        return a, None

    assert get_config_from_stage(rules, B()) == {}
    assert get_config_from_stage(rules, "cello") == 0
    a_func(3)
    assert get_config_from_stage(rules, "cello") == 3


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
    cb_stage = C() / B()
    stage_a.register_depends_on(cb_stage)
    route = stage_a / B()
    assert str(finalize_stage(route)) == str([str(C() / B()), str(A() / B())])


def test_finalize_stage_with_before_and_after():
    ab = A() / B()

    @rules.register(ab, before=C(), after=B())
    def route():
        return ["pass"]
    route()

    result = finalize_stage(ab)
    assert str(result) == "C:A:B:B"


def test_finalize_stage_with_before_after_and_depends_on():
    a_start = A("start")
    ab = a_start / B()

    @rules.config(a_start)
    def conf():
        return None, depends_on_stage(rules, ["C:C"])

    @rules.register(C() / C())
    def c():
        return [None]

    @rules.register(ab, before=C(), after=B())
    def route():
        return ["pass"]
    conf()
    route()
    c()
    assert str(finalize_stage(ab)) == "['C:C', 'C:start:B:B']"


def test_one_can_iter_stagenames_tasks_over_routes():
    route = A().register_tasks([1]) / B("BAS").register_tasks([2])
    actual_iter = [(name, tasks) for name, tasks in route.iter_stagename_task()]
    assert actual_iter == [("A", (1,)), ("A:BAS", (2,))]


def test_iter_over_stagenames_tasks_on_long_chains():
    long_route = A() / (B() / A("A2")) / C("CEND")
    actual_iter = [name for name, _ in long_route.iter_stagename_task()]
    assert actual_iter == [
        "A",
        "A:B",
        "A:B:A2",
        "A:B:A2:CEND"
    ]


def test_route_dependson_protocol():
    ac = A() / C()
    bc = B() / C()
    bc_depends_on_ac = ac % bc
    assert isinstance(bc_depends_on_ac, _RouteChain)
    assert str(bc_depends_on_ac) == "['A:C', 'B:C']"
    with pytest.raises(TypeError):
        A() % bc
