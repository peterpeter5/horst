from click import echo, style
import itertools
from .result import Ok, Error, UpToDate
from contextlib import contextmanager
from functools import partial


class Printer:

    _spinner = itertools.cycle(['-', '/', '|', '\\'])

    def __init__(self, verbose=False):
        self.verbose = verbose

    @contextmanager
    def spinner(self):
        yield self
        echo("\r ", nl=False)
        echo(" ", nl=False)

    def signal_progress(self):

        echo("\r", nl=False)
        echo("\r", nl=False)
        echo(next(self._spinner), nl=False)

    def print_stage(self, stage):
        echo("[stage] [%s]" % stage)
    
    def print_effect_result(self, effect_result):
        _is = partial(isinstance, effect_result)
        if _is(Ok):
            result_format = ("OK", 'green') 
        elif _is(UpToDate):
            result_format = ("UP-TO-DATE", 'yellow')
        else:
            result_format = ("Oooppsala", 'magenta')

        result_str, color = result_format
        echo("\t|--> %s" % style(result_str, fg=color))
