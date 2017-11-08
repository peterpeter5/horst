from functools import singledispatch
from horst.effects import DryRun, RunCommand 
import warnings
import subprocess
from horst.testing import RunPyTest
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
def _run_command(action, printer):
    proc = subprocess.Popen(str(action), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lines = []
    rt_code = None
    with printer.spinner() as spinner:
        for line in iter(partial(proc.stdout.read, 1), ''):
            spinner = spinner(line.decode())
            lines.append(line.decode())
            rt_code = proc.poll()
            if  rt_code is not None and not line:
                break
    error_stream = proc.stderr.readlines()
    result_type = Ok if rt_code == 0 else Error
    return result_type("".join(lines + list(map(lambda x: x.decode(), error_stream))).strip(), rt_code)


@execute.register(RunPyTest)
def _(action, printer):
    result = _run_command(action, printer)
    if result.exit_code == 5:
        return UpToDate("Found no Tests to run")
    else:
        return result


def execute_stage(stage, printer):
    for name, tasks in stage:
        printer.print_stage(name)
        parallel_tasks = tasks if tasks else [_NoOp(name)]
        # TODO execute in parallel!
        for single_task in parallel_tasks:
            result = execute(single_task, printer=printer)
            printer.print_effect_result(single_task, result)
