import click
import os
from functools import partial
from horst import get_horst
from horst.effects import DryRun 
from horst.runner.runner import execute_stage


def exec_file(filename):
    exec(compile(open(filename, "rb").read(),
                 filename, 'exec'), globals(), locals())


class MyCli(click.MultiCommand):

    static_cmds = ["debug"]

    def list_commands(self, ctx):
        dynamic_cmds =  [
            cmd 
            for cmd, tasks in get_horst().get_commands()
            if not all(map(lambda x: len(x) == 0, tasks))
        ]
        return dynamic_cmds + self.static_cmds

    def get_command(self, ctx, name):
        if name in self.static_cmds:
            return self.handle_static(ctx, name)

        translation = dict(get_horst().get_commands())
        _stage = translation[name]
        stage = [
            (":".join(name.split(":")[0:num+1]), tasks if not ctx.params.get('dry', False) else list(map(DryRun, tasks)))
            for num, tasks in enumerate(_stage)
        ]


        func = partial(execute_stage, stage, printer=click.echo)
        return click.Command(name, {}, func)

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
