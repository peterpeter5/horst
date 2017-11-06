from ..effects import EffectBase, DryRun


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