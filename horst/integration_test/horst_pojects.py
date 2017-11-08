import re
from contextlib import contextmanager
from os import path


def get_output_checked(result):
    assert result.exit_code == 0
    output = result.output
    print(output)
    return output


def get_stage_result_from_output(output):
    out_signal = "|-->"
    output_lines = output.splitlines()
    return [
        (re.findall(r"\[stage\] \[(.+)\]", output_lines[number - 1])[0], line.replace(out_signal, "").strip())
        for number, line in enumerate(output_lines)
        if line.startswith("\t%s" % out_signal)
    ]


def get_command_section(output):
    return output.split("Commands:")[-1]


@contextmanager
def horst_project(conf_func, folder):
    conf_func(folder)
    yield path.join(folder, "build.py")


@contextmanager
def isolated_horst_project(conf_func, runner):
    with runner.isolated_filesystem() as folder, horst_project(conf_func, folder):
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


def horst_with_no_tests(folder):
    with open(path.join(folder, "build.py"), 'w') as file:
        file.write("""
from horst import *
from horst import test
Horst(__file__, 'unit')
test()
"""
                   )
    import os
    package_folder = path.join(folder, "unit")
    if not path.exists(package_folder):
        os.mkdir(package_folder)
