from click import echo, style
import itertools
from .result import Ok, Error, UpToDate, Dry
from contextlib import contextmanager
from functools import partial
import time


class Printer:

    _spinner = itertools.cycle(['-', '/', '|', '\\'])

    def __init__(self, verbose=False):
        self.verbose = verbose
        self._progress_line_length = 0

    @contextmanager
    def spinner(self):
        self._progress_line_length = 0
        yield self.signal_progress()
        self._clear_current_line()

    def _clear_current_line(self):
        echo("\r ", nl=False)
        echo(" "*self._progress_line_length, nl=False)
        echo("\r", nl=False)

    def signal_progress(self, line_length=0):
        def _inner(current_char, line_length, clear_line=False):
            if clear_line:
                self._clear_current_line()

            if current_char.splitlines() and not current_char.splitlines()[0]:
                echo("%s " % next(self._spinner), nl=False)
                self._progress_line_length = max(self._progress_line_length, line_length + 10)
                line_length = 0
                clear_line = True
            else:
                echo(str(current_char), nl=False)
                line_length += 1
                clear_line = False
            return partial(_inner, line_length=line_length, clear_line=clear_line)

        return partial(_inner, line_length=line_length)

    def print_stage(self, stage):
        echo("[stage] [%s]" % stage)
    
    def print_effect_result(self, task, task_reslut):
        _is = partial(isinstance, task_reslut)
        if _is(Ok):
            result_format = ("OK", 'green') 
        elif _is(UpToDate):
            result_format = ("UP-TO-DATE", 'yellow')
        elif _is(Dry):
            result_format = ("Tasks that would run:", 'cyan')
        elif _is(Error):
            result_format = ("ERROR", "red", True)
        else:
            result_format = ("Oooppsala", 'magenta')

        result_str, color, *verbose_result = result_format
        echo("\t|--> %s" % style(result_str, fg=color))
        if self.verbose or verbose_result or task.verbose:
            for line in task_reslut.output.splitlines():
                echo(style("\t\t|-->", fg=color) + " %s" % line.strip())
