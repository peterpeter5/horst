from functools import singledispatch
from horst.effects import DryRun, RunCommand 
import warnings


class UptoDate:
    def __init__(self, stage_name):
        self.stage_name = stage_name


@singledispatch
def execute(effect, *args, **kwargs):
    warnings.warn("No Executor specified for action: <%s>" % str(effect.__class__))


@execute.register(DryRun)
def _(action, std_in=None, std_out=None):
    printer = print if std_out is None else std_out
    return str(action)


@execute.register(UptoDate)
def _(action, std_in=None, std_out=None):
    printer = std_out
    return "UP-TO-DATE"


def execute_stage(stage, printer=None):
    print(stage)
    for name, tasks in stage:
        printer("[stage] [%s]" % name)
        parallel_tasks = tasks if tasks else [UptoDate(name)]
        # TODO execute in parallel!
        for single_task in parallel_tasks:
            printer("\t|--> %s" % execute(single_task, std_out=printer))