import re
from collections import defaultdict
from contextlib import contextmanager
from functools import partial
from os import path
import os


def get_output_checked(result):
    assert result.exit_code == 0
    output = result.output
    print(output)
    return output


def get_stage_results(output):
    stage_results = defaultdict(list)
    out_signal = "|-->"

    def nothing(stage, line):
        parsed_stage = re.findall(r"\[stage\] \[(.+)\]", line)
        stage = stage if not parsed_stage else parsed_stage[0]
        if out_signal in line:
            return result(stage, line)
        else:
            return partial(nothing, stage)

    def result(current_stage, line):
        if line.startswith("\t%s" % out_signal):

            linresult = line.replace(out_signal, "").strip()
            regex = re.findall("(\w+)[ ]\[", linresult)
            linresult = regex[0] if regex else linresult
            stage_results[current_stage].append(linresult)
            return partial(result, current_stage)
        elif out_signal in line:
            return partial(result, current_stage)
        else:
            return nothing(current_stage, line)

    parser = nothing("", "")
    for line in output.splitlines():
        parser = parser(line)
    return [
        (name, stage_res[0] if len(stage_res) == 1 else stage_res)
        for name, stage_res in stage_results.items()
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
        os.environ["_TEST_HORST_"] = "True"
        conf_func(folder)
        yield path.join(folder, "build.py")
        os.environ.pop("_TEST_HORST_")


def minimal_horst(folder):
    with open(path.join(folder, "build.py"), "w") as file:
        file.write("""
from horst import *
Horst(__file__, "unit")
package(
    name="unit",
    version="0.0.0",
    description="short",
    long_description="long",
    url="/not/there/",
)
dependencies()
test()

""")
    if not path.exists(path.join(folder, "unit")):
        os.mkdir(path.join(folder, "unit"))
    with open(path.join(folder, "unit", "__init__.py"), "w") as file:
        file.write("  ")



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
    file_name = path.join(folder, "build.py")
    with open(file_name, 'w') as file:
        file.write("""
from horst import *
from horst import test
Horst(__file__, 'unit')
test()
"""
                   )
    package_folder = path.join(folder, "unit")
    if not path.exists(package_folder):
        os.mkdir(package_folder)


def horst_with_tests_that_pass(folder):
    file_name = path.join(folder, "build.py")
    with open(file_name, 'w') as file:
        file.write("""
from horst import *
from horst import test
Horst(__file__, 'unit')
test(funny=pytest())        
"""
                   )
    package_path = path.join(folder, "unit")
    if not path.exists(package_path):
        os.mkdir(package_path)
    with open(path.join(package_path, "__init__.py"), "w") as file:
        file.write(" ")
    with open(path.join(package_path, "test_units.py"), "w") as file:
        file.write("""
def test_i_will_pass():
    assert True
    

def test_pass_every_time():
    assert True
""")


def horst_with_tests_one_pass_one_fail(folder):
    file_name = path.join(folder, "build.py")
    with open(file_name, 'w') as file:
        file.write("""
from horst import *
from horst import test
Horst(__file__, 'unit')
test(unittest=pytest(include=[named("pass")]), unstable=pytest())        
"""
                   )
    package_path = path.join(folder, "unit")
    if not path.exists(package_path):
        os.mkdir(package_path)
    with open(path.join(package_path, "__init__.py"), "w") as file:
        file.write(" ")
    with open(path.join(package_path, "test_pass.py"), "w") as file:
        file.write("""
def test_i_will_pass():
    assert True


def test_pass_every_time():
    assert True
""")
    with open(path.join(package_path, "test_fail.py"), "w") as file:
        file.write("""
def test_i_will_fail():
    assert False
""")


def horst_with_test_that_fail(folder):
    file_name = path.join(folder, "build.py")
    with open(file_name, 'w') as file:
        file.write("""
from horst import *
from horst import test
Horst(__file__, 'unit')
test()        
"""
                   )
    package_path = path.join(folder, "unit")
    if not path.exists(package_path):
        os.mkdir(package_path)
    with open(path.join(package_path, "__init__.py"), "w") as file:
        file.write(" ")
    with open(path.join(package_path, "test_units.py"), "w") as file:
        file.write("""
def test_i_will_pass():
    assert True


def test_pass_every_time():
    assert False
    """)
