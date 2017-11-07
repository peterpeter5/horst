from functools import singledispatch
from horst.effects import DryRun, RunCommand 
import warnings
import subprocess
import itertools
from functools import partial
from .result import Ok, Error, UpToDate, Dry


class _NoOp:
    verbose = False

    def __init__(self, stage_name):
        self.stage_name = stage_name


@singledispatch
def execute(effect, *args, **kwargs):
    warnings.warn("No Executor specified for action: <%s>" % str(effect.__class__))
    return -1, None


@execute.register(DryRun)
def _(action, printer):
    return Dry(str(action.__display__()))


@execute.register(_NoOp)
def _(action, printer):
    return UpToDate("")


@execute.register(RunCommand)
def _(action, printer):
    proc = subprocess.Popen(str(action), shell=True, stdout=subprocess.PIPE)
    lines = []
    rt_code = None
    with printer.spinner() as spinner:
        for line in iter(partial(proc.stdout.read, 1), ''):
            spinner = spinner(line.decode())
            lines.append(line.decode())
            rt_code = proc.poll()
            if  rt_code is not None:
                break
    
    result_type = Ok if rt_code == 0 else Error
    return result_type("".join(lines))


def execute_stage(stage, printer):
    for name, tasks in stage:
        printer.print_stage("[stage] [%s]" % name)
        parallel_tasks = tasks if tasks else [_NoOp(name)]
        # TODO execute in parallel!
        for single_task in parallel_tasks:
            result = execute(single_task, printer=printer)
            printer.print_effect_result(single_task, result)
