import shutil
from functools import singledispatch
from horst import get_project_path
from horst.effects import DryRun, RunCommand, UpdateFile, CreateFile, DeleteFileOrFolder
import warnings
import subprocess
from horst.testing import RunPyTest
from functools import partial
from .result import Ok, Error, UpToDate, Dry
from os import path
import os


class _NoOp:
    verbose = False

    def __init__(self, stage_name):
        self.stage_name = stage_name


@singledispatch
def execute(effect, *args, **kwargs):
    warnings.warn("No Executor specified for action: <%s>" % str(effect.__class__))
    return Error("No Runner defined for action: <%s>" % str(effect.__class__))


@execute.register(DryRun)
def _(action, printer):
    return Dry(str(action.__display__()))


@execute.register(_NoOp)
def _(action, printer):
    return UpToDate("")


@execute.register(RunCommand)
def _run_command(action, printer):
    proc = subprocess.Popen(
        str(action),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=get_project_path()
    )
    lines = []
    rt_code = None
    with printer.spinner() as spinner:
        for line in iter(partial(proc.stdout.read, 1), ''):
            spinner = spinner(line.decode())
            lines.append(line.decode())
            rt_code = proc.poll()
            if rt_code is not None and not line:
                break
    error_stream = proc.stderr.readlines()
    result_type = Ok if rt_code == 0 else Error
    content = "".join(lines + list(map(lambda x: x.decode(), error_stream))).strip()
    return result_type(content, rt_code)


@execute.register(RunPyTest)
def _(action, printer):
    result = _run_command(action, printer)
    if result.exit_code == 5:
        return UpToDate("Found no Tests to run")
    else:
        return result


@execute.register(UpdateFile)
@execute.register(CreateFile)
def _(action, printer):
    """
    :type action: UpdateFile|CreateFile
    :param printer:
    :return:
    """
    try:
        with open(action.file_path, "w") as file:
            file.write(action.content)
            return Ok("Updated file: %s" % action.file_path)
    except (FileNotFoundError, PermissionError) as error:
        return Error(repr(error))


@execute.register(DeleteFileOrFolder)
def _(action, printer):
    abspath = action.file_of_folder
    _type, delete = ("Folder", shutil.rmtree) if path.isdir(abspath) else ("File", os.remove)
    try:
        delete(abspath)
        return Ok("Deleted %s" % _type)

    except (FileNotFoundError, PermissionError) as error:
        return Error(repr(error))


def execute_stage(stage, printer):
    named_results = []
    stop_stage = False
    for name, tasks in stage:
        printer.print_stage(name)
        parallel_tasks = tasks if tasks else [_NoOp(name)]
        # TODO execute in parallel!
        for single_task in parallel_tasks:
            result = execute(single_task, printer=printer)
            printer.print_effect_result(single_task, result)
            named_results.append((name, result))
            if isinstance(result, Error):
                stop_stage = True
        if stop_stage:
            break

    return named_results
