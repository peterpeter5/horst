from .horst import get_horst, get_project_path
from horst.effects import EffectBase, ErrorBase, RunCommand
import re
import os
from .rules import root, env, create, update
from functools import reduce


class Versioning(EffectBase):
    def __init__(self, commands):
        self.commands = commands


def package(name, version):
    horst = get_horst()
    horst.register_release(Versioning(version))


class CreateEnv(RunCommand):

    def __init__(self, virt_env_path, executable):
        super(CreateEnv, self).__init__("virtualenv",
                                        ("-p %s" % executable, virt_env_path))

    def __repr__(self):
        return str(self)


class UpdateEnv(RunCommand):
    def __init__(self, virt_env_path, dependencies):
        pip_part = ("bin", "pip") if _is_linux() else ("scripts", "pip")
        self.pip = os.path.join(virt_env_path, *pip_part)
        self.dependencies = dependencies
        super(UpdateEnv, self).__init__("%s install --upgrade" % self.pip, dependencies)

    def __display__(self):
        return "pip install %s" % " ".join(self.dependencies)


def _is_linux():
    return os.name == 'posix'


@root.config
def virtualenv(config=None):
    if config is None:
        config = {".env": {"python": "python"}}
    for name, config in config.items():
        config = {'name': name, **config}
    _create_environment(config)
    return config


@root.register(env / create)
def _create_environment(virtenv_config):
    env_base_path = os.path.join(get_project_path(), virtenv_config['name'])
    tasks = []
    if _is_linux():
        check_path = os.path.join(env_base_path, "bin", "python")
    else:
        check_path = os.path.join(env_base_path, "scripts", "python.exe")
    if not os.path.exists(check_path):
        tasks.append(CreateEnv(env_base_path, virtenv_config['python']))

    return tasks


@root.register(env / create / update, route="env/update")
def _update_environment(deps, virtenv):
    env_base = os.path.abspath(os.path.join(get_project_path(), virtenv['name']))
    deps_to_install = reduce(
        lambda state, deps: state + deps, deps.values(), [])
    return [UpdateEnv(env_base, deps_to_install)] if deps_to_install else []


@root.config
def dependencies(install=[], build=[], test=[], versions=[], environment=virtualenv()):
    deps = dict(
        install=install,
        build=build,
        test=test,
        versions=versions
    )
    _update_environment(deps, environment)
    return deps
