import subprocess

from horst import get_horst, get_project_path
from horst.effects import EffectBase, CreateFile, UpdateFile, RunCommand, DeleteFileOrFolder
from .rules import root, build, create_setup, update_setup, run_setup, clean_up
from os import path

_here = path.dirname(__file__)


class Versioning(EffectBase):
    def __init__(self, commands):
        self.commands = commands


def from_git_config(*values):
    project_path = get_project_path()
    result = subprocess.run(
        "git config -l",
        shell=True,
        stdout=subprocess.PIPE,
        check=True,
        cwd=project_path
    )
    # TODO cache result...
    return {
        val: line.split("=")[1]
        for line in result.stdout.decode().splitlines()
        for val in values
        if val in line
    }


@root.config(build)
def package(name, version, description, long_description=None, url=None):
    project_path = get_project_path()
    path_to_setup = path.join(project_path, "setup.py")
    setup_config = dict(
        name=name,
        version=version,
        description=description,
        long_description=long_description,
        url=url
    )
    _create_setup(path_to_setup)
    _update_setup(path_to_setup, setup_config)
    _run_bdist_wheel()
    _clean_install_fragments()
    return setup_config


@root.register(build / create_setup)
def _create_setup(setup_path):
    return [CreateFile(setup_path, " ")] if not path.exists(setup_path) else []


@root.register(build / create_setup / update_setup, "build/update_setup")
def _update_setup(setup_path, config):
    # TODO sanity_check
    content = _render_setuppy(config)
    return [UpdateFile(setup_path, content)]


@root.register(build / create_setup / update_setup / run_setup, "build/wheel")
def _run_bdist_wheel(clean_intermediates=True):
    clean_up = [] if not clean_intermediates else _clean_install_fragments()

    return [RunCommand("python", ["setup.py", "bdist_wheel"])] + clean_up


def _clean_install_fragments():
    folders = ["build", "%s.egg-info" % get_horst().package_name]
    project_base_path = get_project_path()
    return [DeleteFileOrFolder(path.join(project_base_path, folder)) for folder in folders]


def _render_setuppy(config):
    with open(path.join(_here, "templates", "setuppy.template")) as file:
        content = file.read()

    formatted_content = content.format(**config)
    return formatted_content
