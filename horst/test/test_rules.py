from ..rules import Engine, _Stage
import pytest


class A(_Stage):
    pass


class B(_Stage):
    pass

rules = Engine()
_ab_stage = A() / B()

@rules.config
def config_smthng(a, b):
    return [a, b]

@rules.register(_ab_stage)
def put_tasks_on_b():
    return ["b"]


def test_config_function_reslut_is_saved_in_engine():
    config_smthng("a", 2)
    assert rules._config == {'config_smthng': ['a', 2]}


def test_stage_div_protocol_with_wrong_types():
    with pytest.raises(TypeError):
        7 / A() 

def test_stage_div_protocol_and_string_serialization():
    assert str(A() / B() / B() / A()) == "A.B.B.A"

def test_stages_can_register_tasks():
    a = A()
    a.register_tasks(["a"])
    assert a._tasks == ["a"]
    
    ab = a / B()
    ab.register_tasks(["a", "b"])
    ab_chain = list(ab)
    assert ab_chain[0]._tasks == ["a"]
    assert ab_chain[1]._tasks == ["a", "b"]

def test_stages_give_a_tasks_chain_when_asked():
    a = A()
    a.register_tasks(["a"])
    
    ab = a / B()
    ab.register_tasks((["a"], ["b"]))
    assert ab.tasks == [
        ["a"], 
        (["a"], ["b"])
    ]
    

def test_rules_register_decorator_puts_config_results_on_stage():
    put_tasks_on_b()
    expected_tasks = [[], ["b"]]
    assert _ab_stage.tasks == expected_tasks
    assert rules._stages == {"A.B": expected_tasks}