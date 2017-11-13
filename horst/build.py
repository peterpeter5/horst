import subprocess

from setuptools import find_packages

from horst import get_horst, get_project_path
from horst.effects import EffectBase, CreateFile, UpdateFile, RunCommand, DeleteFileOrFolder, StageConfigError
from horst.release import release, release_route
from .rules import root, build, create_setup, update_setup, run_setup, configure_or_default, depends_on_stage, \
    get_config_from_stage, env, setup
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
def package(name=None, version=None, description=None, long_description=None, url=None, packages=None, releases=None):
    if name and version and description is None:
        yield StageConfigError("<name, version, description> must be specfied via <package>")

    long_description = string_or_return_empty_one(long_description)
    url = string_or_return_empty_one(url)
    project_path = get_project_path()
    packages = configure_or_default(packages, find_packages)
    path_to_setup = path.join(project_path, "setup.py")
    setup_config = dict(
        name=name,
        version=version,
        description=description,
        long_description=long_description,
        url=url,
        packages=packages,
    )
    releases = configure_or_default(releases, release)
    yield setup_config, depends_on_stage(root, ["test:build", "test:all", "test"])
    install_dependencies = get_config_from_stage(root, env)
    build_options = get_config_from_stage(root, release_route)
    setup_config.update({'install_requires': install_dependencies["install"]})
    _create_setup(path_to_setup)
    _update_setup(path_to_setup, setup_config)
    _run_bdist_wheel(build_options)
    _clean_install_fragments()


def string_or_return_empty_one(value):
    return value if isinstance(value, str) else ""


@root.register(setup / create_setup)
def _create_setup(setup_path):
    return [CreateFile(setup_path, " ")] if not path.exists(setup_path) else []


@root.register(setup / create_setup / update_setup, "build/update/setup")
def _update_setup(setup_path, config):
    # TODO sanity_check
    content = _render_setuppy(config)
    return [UpdateFile(setup_path, content)]


@root.register(build / create_setup / update_setup / run_setup, "build/wheel")
def _run_bdist_wheel(build_options=None, clean_intermediates=True):
    build_options = build_options if build_options is not None else []
    clean_up = [] if not clean_intermediates else _clean_install_fragments()

    return [RunCommand("python", ["setup.py", "bdist_wheel"] + build_options)] + clean_up


def _clean_install_fragments():
    folders = ["build", "%s.egg-info" % get_horst().package_name]
    project_base_path = get_project_path()
    return [DeleteFileOrFolder(path.join(project_base_path, folder)) for folder in folders]


def _render_setuppy(config):
    with open(path.join(_here, "templates", "setuppy.template")) as file:
        content = file.read()

    formatted_content = content.format(**config)
    return formatted_content
