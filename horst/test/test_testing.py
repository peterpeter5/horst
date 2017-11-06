from ..testing import Mark, marked_as, MarkOptionList, not_marked_as, NamePattern, NamesList, named, junit, pytest_coverage
from ..effects import RunOption
from functools import reduce
import pytest


def test_mark_option_serializes_as_expected():
    slow = Mark("slow")
    assert str(slow) == '-m="slow"'


def test_mark_option_is_invertable_via_bit_operator():
    fast = Mark("fast")
    assert str(fast.invert()) == '-m="not (fast)"'


def test_mark_options_can_be_used_with_bit_and():
    fast = Mark("fast")
    slow = Mark("slow")
    assert '-m="(fast) and (slow)"' == str(fast & slow)


def test_mark_options_can_be_used_with_bit_or():
    fast = Mark("fast")
    slow = Mark("slow")
    assert '-m="fast or slow"' == str(fast | slow)


def test_marked_as_reutrns_a_marklist():
    mixed = marked_as("slow", "fast")
    assert isinstance(mixed, MarkOptionList)
    assert len(mixed) == 2


@pytest.fixture
def marks():
    return MarkOptionList([Mark("a"), Mark("b")])


def test_marklist_list_protocol(marks):
    assert len(marks) == 2
    for m in marks:
        assert m in list(marks)


def test_marklist_to_mark_returns_or_marks(marks):
    assert marks.to_option() == Mark("a") | Mark("b")
    assert MarkOptionList([Mark("c")]).to_option() == Mark("c")
 

def test_marklist_can_be_inverted(marks):
    assert marks.invert().value == "not (a or b)"


def test_marklist_can_be_used_with_and(marks):
    cs = MarkOptionList([Mark("c")])
    assert (cs & marks).value == "(c) and (a or b)"


def test_marked_as_returns_marklist_options():
    mixed = marked_as("a", "b")
    assert mixed == MarkOptionList([Mark("a"), Mark("b")])


def test_complex_markas_example():
    complex_mark = marked_as("slow", "load") & not_marked_as("fast", "prio") | marked_as("always")
    expected_option = '-m="(slow or load) and (not (fast or prio)) or always"'
    assert str(complex_mark) == expected_option


def test_namepattern_serializes_as_expected():
    loadtest = NamePattern("loadtest")
    assert str(loadtest) == '-k="loadtest"'
    durability = NamePattern("durability")
    assert str(loadtest & durability) == '-k="(loadtest) and (durability)"'


def test_junit_serializes_as_expected():
    assert junit() == []
    assert junit("a") == [RunOption("junit-xml", "a")]
    assert junit("a", "b") == [RunOption("junit-xml", "a"), RunOption("junit-prefix", "b")]


def test_pytest_coverage_with_config_file():
    assert pytest_coverage(config=".asdf.conf") == [RunOption("cov-config", ".asdf.conf")]


def test_pytest_coverage_with_full_config():
    cover_config = pytest_coverage("package", ["html", "term"], 96)
    assert cover_config == [
        RunOption('cov', 'package'), 
        RunOption('cov-report', 'html'),
        RunOption('cov-report', 'term'),
        RunOption('cov-fail-under', '96')
    ]