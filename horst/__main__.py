import click
import os
from functools import partial, reduce
from horst import get_horst
from horst.effects import DryRun 
from horst.runner.runner import execute_stage


def exec_file(filename):
    exec(compile(open(filename, "rb").read(),
                 filename, 'exec'), globals(), locals())


class MyCli(click.MultiCommand):

    def list_commands(self, ctx):
        # print("list command", ctx)
        return [cmd for cmd, _ in get_horst().get_commands()]


    def get_command(self, ctx, name):
        translation = dict(get_horst().get_commands())
        _stage = translation[name]
        stage = [
            (":".join(name.split(":")[0:num+1]), tasks if not ctx.params.get('dry', False) else list(map(DryRun, tasks)))
            for num, tasks in enumerate(_stage)
        ]


        func = partial(execute_stage, stage, printer=click.echo)
        return click.Command(name, {}, func)


#@click.command(cls=cli)
def debug():
    print("===== CONFIG =====")
    print(root._config)
    print(" = = = = = = = = = ")
    print("===== STAGES =====")
    print(root._stages)
    print("= = = = = = = = = = ")


if __name__ == "__main__":
    current_dir = os.getcwd()
    local_build_file = os.path.join(current_dir, "build.py")
    if os.path.exists(local_build_file):
        exec_file(local_build_file)
        #for task in get_horst().get_tasks():
        #    shout_name = functools.partial(print, task)
        #    cli.command(task)(shout_name)
    params = [click.Option(param_decls=["-d", "--dry"], is_flag=True, default=False, help="DryRun nothing will be executed")]
    cli = MyCli(params=params)
    cli()
