from .effects import RunOption
from functools import partial, reduce
from itertools import chain
from .rules import root, integration_test, unittest
from .rules import test as test_route
from .horst import get_project_path, get_horst
from .effects import RunCommand
from os import path


def _make_option_or_empty_list(name, value):
    return [RunOption(name, value)] if value else [] 



def flatten(args):
    return list(chain(*args))

class _LogicalOption(RunOption):

    def invert(self):
        formatter = self._enclose_with_parentheses if " and " in self.value or " or " in self.value else lambda x:x
        return self.__class__("not %s" % formatter(self.value))

    def __eq__(self, other):
        return str(self) == str(other)

    def __and__(self, other):
        
        format_self, format_other = [
            self._enclose_with_parentheses if "and" in logic.value or "or" in logic.value else lambda x:x
            for logic in (self, other)
        ]
        new_value = "%s and %s" % (format_self(self.value), format_other(other.to_option().value))
        return self.__class__(new_value)

    def __or__(self, other):
        return self.__class__("%s or %s" % (self.value, other.to_option().value))

    def to_option(self):
        return self

    def _enclose_with_parentheses(self, text):
        return "(%s)" % str(text)


class _LogicalOptionList:
    def __init__(self, iterable):
        self._options = list(iterable)

    def __iter__(self):
        return (a for a in self._options)

    def __len__(self):
        return len(self._options)

    def to_option(self):
        return reduce(lambda x, y: x | y, self)

    def __str__(self):
        return str(self.to_option)

    def invert(self):
        return self.to_option().invert()

    def __and__(self, other):
        return self.to_option() & other.to_option()

    def __eq__(self, other):
        return self.to_option() == other.to_option()


class Mark(_LogicalOption):
    def __init__(self, value):
        super(Mark, self).__init__("m", value, hyphens=1)


class MarkOptionList(_LogicalOptionList):
    pass


class NamePattern(_LogicalOption):
    def __init__(self, name):
        super(NamePattern, self).__init__("k", name, hyphens=1)


class NamesList(_LogicalOptionList):
    pass


def marked_as(*args):
    return MarkOptionList(map(Mark, args))


def not_marked_as(*args):
    return marked_as(*args).invert()


def named(*args):
    return NamesList(map(NamePattern, args))


def junit(path=None, prefix=None):
    report_path = _make_option_or_empty_list("junit-xml", path)
    prefix = _make_option_or_empty_list("junit-prefix", prefix)
    # TODO Error-handling: raise  error when (not report_path and prefix)
    return report_path + prefix


def pytest_coverage(folders=None, report=[], min=None, config=None, disable=False):
    if disable:
        return []

    if config is not None:
        if folders or report or min:
            pass  # TODO Error-handling raise error
        return _make_option_or_empty_list("cov-config", config)

    folders = [folders] if not isinstance(folders, (list, tuple)) else folders
    folders = [RunOption("cov", folder) for folder in folders]
    
    report = flatten([_make_option_or_empty_list("cov-report", report_type) for report_type in report])
    break_on_min = _make_option_or_empty_list("cov-fail-under", min)
    return folders + report + break_on_min


def pytest(folders="", exclude=[], include=[], report=[], coverage=pytest_coverage()):
    base_path = get_project_path()
    folders = [get_horst().package_name] if not folders else folders
    folders = [
        path.join(base_path, folder)
        for folder in ([folders] if not isinstance(folders, (list, tuple)) else folders)
    ]
    excludes = [ex.invert() for ex in exclude]
    inclu_exclu_marks, inclu_exclu_names = _join_detection_config(excludes, include)
    return inclu_exclu_marks + inclu_exclu_names + report + coverage + folders


def _join_detection_config(excludes, includes):
    is_mark = lambda x: isinstance(x, Mark)
    is_name_pattern = lambda x: isinstance(x, NamePattern)
    exclude_marks = list(filter(is_mark, excludes))
    include_makrs = list(filter(is_mark, includes))
    if include_makrs and exclude_marks:
        inclu_exclu = [exclude_marks[0] & include_makrs[0]]
    else:
        inclu_exclu = include_makrs + exclude_marks

    exclude_names = list(filter(is_name_pattern, excludes))
    include_names = list(filter(is_name_pattern, includes))
    if include_names and exclude_names:
        inclu_exclu_names = [exclude_names[0] & include_names[0]]
    else:
        inclu_exclu_names = include_names + exclude_names  
    return inclu_exclu, inclu_exclu_names


class RunPyTest(RunCommand):
    verbose = True
    
    def __init__(self, options):
        super(RunPyTest, self).__init__("pytest", options)



@root.config
def test(unittest=pytest(), **kwags):
    _run_unittest(unittest)
    return {'unittest': unittest}


@root.register(test_route/unittest, route="test")
def _run_unittest(unittest_config):
    return [RunPyTest(unittest_config + ["--color=yes"])]

