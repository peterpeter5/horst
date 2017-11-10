import subprocess

from horst import get_horst, get_project_path
from horst.effects import EffectBase
from .rules import root, build


class Versioning(EffectBase):
    def __init__(self, commands):
        self.commands = commands


def from_git_config(*values):
    def one_of_in(line, values):
        return any(val in line for val in values)
    project_path = get_project_path()
    result = subprocess.run(
        "git config -l",
        shell=True,
        stdout=subprocess.PIPE,
        check=True,
        cwd=project_path
    )
    return {
        val: line.split("=")[1]
        for line in result.stdout.decode().splitlines()
        for val in values
        if val in line
    }



@root.config(build)
def package(name, version, description, long_description=None, url=None):
    horst = get_horst()
    horst.register_release(Versioning(version))