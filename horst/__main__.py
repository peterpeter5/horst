import click
import os
from functools import partial
from horst import get_horst
from horst.effects import DryRun
from horst.rules import finalize_stage
from horst.runner.result import Error
from horst.runner.runner import execute_stage
from horst.runner.printer import Printer
from functools import partial
from copy import copy
from horst.horst import get_horst


def exec_file(filename):
    global_attributes = copy(globals())
    global_attributes["__file__"] = filename
    get_horst()._invalidate()
    exec(
        compile(
            open(filename, "rb").read(),
            filename,
            'exec'
        ), global_attributes, locals())


def result_handler(func):
    def interpret(stage, result):
        if isinstance(result, Error):
            raise click.ClickException("Error during execution of stage: %s" % stage)
        else:
            pass

    return [interpret(name, result) for name, result in func()]


class MyCli(click.MultiCommand):
    static_cmds = ["debug"]

    def __init__(self, build_file="", *args, **kwargs):
        if os.path.exists(build_file):
            exec_file(build_file)
        super(MyCli, self).__init__(*args, **kwargs)

    def list_commands(self, ctx):
        dynamic_cmds = [
            cmd
            for cmd, stage in get_horst().get_commands().items()
            if not all(map(lambda x: len(x) == 0, stage.tasks))
        ]
        return dynamic_cmds + self.static_cmds

    def get_command(self, ctx, name):
        if name in self.static_cmds:
            return self.handle_static(ctx, name)
        is_dry_run = ctx.params.get('dry', False)
        is_verbose = ctx.params.get('verbose', False)
        translation = get_horst().get_commands()
        stage = translation[name]
        task_transformation = (lambda x: x) if not is_dry_run else (lambda x: DryRun(x))
        stage = finalize_stage(stage, task_transformation)

        gui = Printer(is_dry_run or is_verbose)
        func = partial(execute_stage, stage, printer=gui)
        return click.Command(name, {}, partial(result_handler, func))

    def handle_static(self, ctx, name):
        if "debug" == name:
            return debug


@click.command()
def debug():
    state = get_horst().get_horst_state()
    print("===== CONFIG =====")
    print(state['config'])
    print(" = = = = = = = = = ")
    print("===== STAGES =====")
    print(state['stages'])
    print("= = = = = = = = = = ")


params = [
    click.Option(param_decls=["-d", "--dry"], is_flag=True, default=False, help="DryRun nothing will be executed"),
    click.Option(param_decls=["-v", "--verbose"], is_flag=True, default=False, help="Output everything to cli")
]

cli = partial(MyCli, params=params)

if __name__ == "__main__":
    current_dir = os.getcwd()
    local_build_file = os.path.join(current_dir, "build.py")
    cli(local_build_file)()
