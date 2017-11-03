import click
import os
import functools
from horst import get_horst


def exec_file(filename):
    exec(compile(open(filename, "rb").read(),
                 filename, 'exec'), globals(), locals())


@click.group()
def cli():
    click.echo("main")


@cli.command()
def tasks():

    click.echo("RELEASE")
    horst = get_horst()
    click.echo(str(horst.get_tasks()))


class FuncWrapper:
    def __init__(self, name, func):
        self.name = name
        self.func = func

    def __name__(self):
        print("__NAME CALLED __")
        return self.name

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


if __name__ == "__main__":
    current_dir = os.getcwd()
    local_build_file = os.path.join(current_dir, "build.py")
    if os.path.exists(local_build_file):
        exec_file(local_build_file)
        for task in get_horst().get_tasks():
            shout_name = functools.partial(print, task)
            cli.command(task)(shout_name)
    cli()
