from .effects import RunOption
from functools import partial, reduce
from itertools import chain


class _LogicalOption(RunOption):

    def invert(self):
        return self.__class__("not (%s)" % self.value)

    def __eq__(self, other):
        return str(self) == str(other)

    def __and__(self, other):
        new_value = "(%s) and (%s)" % (self.value, other.to_option().value)
        return self.__class__(new_value)

    def __or__(self, other):
        return self.__class__("%s or %s" % (self.value, other.to_option().value))

    def to_option(self):
        return self


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


def pytest_coverage(folders=None, report=None, min=None, config=None):
    if config is not None:
        if folders or report or min:
            pass  # TODO Error-handling raise error
        return _make_option_or_empty_list("cov-config", config)

    folders = [folders] if not isinstance(folders, (list, tuple)) else folders
    folders = [RunOption("cov", folder) for folder in folders]
    
    report = flatten([_make_option_or_empty_list("cov-report", report_type) for report_type in report])
    break_on_min = _make_option_or_empty_list("cov-fail-under", min)
    return folders + report + break_on_min


def _make_option_or_empty_list(name, value):
    return [RunOption(name, value)] if value else [] 


def flatten(args):
    return list(chain(*args))
