from ..effects import EffectBase, DryRun, RunOption, RunCommand


class A(EffectBase):
    pass


class WithARepr:

    def __repr__(self):
        return "A"


def test_the_repr_of_effect_base_is_the_class_name():
    assert "A" == repr(A())


def test_the_str_of_effect_base_is_repr():
    assert repr(A()) == str(A())


def test_effects_are_equal_when_reper_is_equal():
    assert A() == WithARepr()


def test_dry_run_is_an_transparent_proxy_for_an_effect():
    a = A()
    assert str(a) == str(DryRun(a))


def test_effect_and_dry_implement_display_protocol():
    a = A()
    d = DryRun(a)
    assert a.__display__() == d.__display__() 


def test_run_option_implements_str_protocol():
    a_option = RunOption("asdf", "a")
    assert '--asdf="a"' == str(a_option)


def test_run_option_num_of_hyphens_can_be_specified():
    option = RunOption("a", 2, 3)
    assert '---a="2"' == str(option)


def test_run_option_without_value_is_interpreted_as_switch():
    option = RunOption("f")
    assert "-f" == str(option)

def test_run_option_can_be_combined_with_run_command():
    option_f = RunOption("f", True)
    option_r = RunOption("r", hyphens=2)
    rm_cmd = RunCommand("rm", [option_f, option_r])
    assert 'rm -f="True" --r' == str(rm_cmd)