from .effects import RunOption
from functools import partial, reduce


class Mark(RunOption):
    def __init__(self, value):
        super(Mark, self).__init__("m", value, hyphens=1)

    def invert(self):
        return Mark("not (%s)" % self.value)

    def __eq__(self, other):
        return str(self) == str(other)

    def __and__(self, other):

        new_value = "(%s) and (%s)" % (self.value, other.to_mark().value)
        return Mark(new_value)

    def __or__(self, other):
        return Mark("%s or %s" % (self.value, other.to_mark().value))

    def to_mark(self):
        return self


class MarkList:
    def __init__(self, iterable):
        self._marks = list(iterable)

    def __iter__(self):
        return (a for a in self._marks)

    def __len__(self):
        return len(self._marks)

    def to_mark(self):
        return reduce(lambda x, y: x | y, self)

    def __str__(self):
        return str(self.to_mark)

    def invert(self):
        return self.to_mark().invert()

    def __and__(self, other):
        return self.to_mark() & other.to_mark()

    def __eq__(self, other):
        return self.to_mark() == other.to_mark()


def marked_as(*args):
    return MarkList(map(Mark, args))

def not_marked_as(*args):
    return marked_as(*args).invert()
