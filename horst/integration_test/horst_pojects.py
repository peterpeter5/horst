from contextlib import contextmanager
from os import path


@contextmanager
def horst_project(conf_func, folder):
    conf_func(folder)
    yield path.join(folder, "build.py")


def minimal_horst(folder):
    with open(path.join(folder, "build.py"), "w") as file:
        file.write("""
from horst import *
Horst(__file__)

dependencies(environment=virtualenv())

""")

def horst_with_dependencies(folder):
    with open(path.join(folder, "build.py"), "w") as file:
        file.write("""
from horst import *
Horst(__file__)

dependencies(install=['pyredux'], environment=virtualenv())

""")
    with open(path.join(folder, "file_with_dependency.py"), "w") as file:
        file.write("""from pyredux import *""")

