from click import echo, style
import click
import itertools
from .result import Ok, Error, UpToDate, Dry
from contextlib import contextmanager
from functools import partial
import os
from shutil import get_terminal_size


class Printer:

    _spinner = itertools.cycle(['-', '/', '|', '\\'])

    def __init__(self, verbose=False):
        self.verbose = verbose
        self._progress_line_length = 0

    @contextmanager
    def spinner(self):
        def noop(y=0):
            return noop

        self._progress_line_length = 0
        size = get_terminal_size((20, 20)).columns - 2
        stream = click.get_binary_stream("stdout")
        isatty = stream.isatty() or os.environ.get("_TEST_HORST_", False)
        yield noop(0) if not isatty else self.signal_progress(0, size)
        # print("max len", size)
        self._clear_current_line(size) if isatty else noop()

    def _clear_current_line(self, current_line_length=None):
        len_to_kill = current_line_length
        echo("\r ", nl=False)
        echo(" "*len_to_kill, nl=False)
        echo("\r", nl=False)
        # print(f"clear line: len: {len_to_kill}")

    def signal_progress(self, line_length=0, max_len=80):

        def _is_new_line_char(current_char):
            if current_char.splitlines() and not current_char.splitlines()[0]:
                return True
            else:
                return False

        def print_new_line(current_line_length, current_char):
            if _is_new_line_char(current_char):
                return partial(print_new_line, current_line_length)

            self._clear_current_line(current_line_length)
            content = "(%s) %s" % (next(self._spinner), current_char)
            echo(content, nl=False)
            return partial(print_char_in_line, len(content))

        def print_char_in_line(current_line_length, current_char):
            content = str(current_char).strip() if current_line_length < max_len else ''
            current_line_length = min(current_line_length + len(content), max_len)

            if _is_new_line_char(current_char):
                return partial(print_new_line, current_line_length)
            
            echo(content, nl=False)
            return partial(print_char_in_line, current_line_length)

        return partial(print_new_line, line_length)

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
