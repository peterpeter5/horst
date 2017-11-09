from horst.rules import root
from ..testing import Mark, marked_as, MarkOptionList, not_marked_as, NamePattern, NamesList, named, junit, \
    pytest_coverage, test
from ..testing import pytest as pytest_config
from ..effects import RunOption
from ..horst import Horst
from functools import reduce
import pytest
from os import path


def test_mark_option_serializes_as_expected():
    slow = Mark("slow")
    assert str(slow) == '-m="slow"'


def test_mark_option_is_invertable_via_bit_operator():
    fast = Mark("fast")
    assert str(fast.invert()) == '-m="not fast"'


def test_mark_options_can_be_used_with_bit_and():
    fast = Mark("fast")
    slow = Mark("slow")
    assert '-m="fast and slow"' == str(fast & slow)


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
    assert (cs & marks).value == "c and (a or b)"


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
    assert str(loadtest & durability) == '-k="loadtest and durability"'


def test_namepattern_inverts_special():
    loadtest = NamePattern("loadtest")
    assert str(loadtest.invert()) == '-k="not loadtest"'
    durability = NamePattern("durability")
    assert str((loadtest & durability).invert()) == '-k="not (loadtest and durability)"'
    assert str((loadtest & (loadtest | durability)).invert()) == '-k="not (loadtest and (loadtest or durability))"'


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


@pytest.fixture(autouse=True)
def horst():
    horst = Horst("")
    horst._invalidate()
    return Horst(__file__, "package_name")


def test_pytest_without_config(horst):
    empty_config = pytest_config()
    assert empty_config == ["package_name"]


def test_pytest_with_config(horst):
    config = pytest_config(
        ["unittest", "test"],
        [marked_as("slow"), named("super_slow")],
        [not_marked_as("load")],
        junit(".junit"),
        pytest_coverage(disable=True)
    )
    folders = ["unittest", "test"]
    assert config == [
        Mark("slow").invert() & Mark("load").invert(),
        NamePattern("super_slow").invert(),
        RunOption("junit-xml", ".junit"),
        *folders
    ]


def test_testconfigure_with_default_test_stages():
    config = test()
    assert config == {"unittest": pytest_config()}
    assert "test" in root.get_stages()


def test_testconfigure_with_multiple_test_stages():
    integration_test_config = pytest_config(folders="integrationtest")
    config = test(integrationtest=integration_test_config)
    unittest_config = pytest_config()
    assert is_subset({"unittest": unittest_config, "integrationtest": integration_test_config}, config)
    stages = root.get_stages()
    assert "test" in stages
    assert "test:integrationtest" in stages


def test_testconfigure_with_multiple_adds_magic_all_stage():
    integration_test_config = pytest_config(folders="integrationtest")
    test(integrationtest=integration_test_config)
    stages = root.get_stages()
    assert "test:all" in stages
    assert len(stages["test:all"].tasks) == 2


def is_subset(a_dict, superset_dict):
    return all(name in superset_dict and superset_dict[name] == value for name, value in a_dict.items())