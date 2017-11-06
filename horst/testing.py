from .effects import RunOption
from functools import partial, reduce


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
    report_path = [RunOption("junit-xml", path)] if path else []
    prefix = [RunOption("junit-prefix", prefix)] if prefix else []
    #TODO Error-handling: raise  error when (not report_path and prefix)
    return report_path + prefix
