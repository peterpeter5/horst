import tempfile

from os import path
import os

from horst import get_horst
from horst.effects import RunOption, Printer, CopyTree, NoOperation
from horst.python import CreateEnv, UpdateEnv
from .rules import root, configure_or_default, depends_on_stage, test_release, get_config_from_stage, env, create, \
    build, release_route, wheel_route, test


def wheel(py_versions=None, universal=False):
    if py_versions is None and universal is False:
        return []
    py_versions = py_versions if isinstance(py_versions, (list, tuple)) else [py_versions]
    build_option = [RunOption("python-tag", ",".join(py_versions)) if not universal else RunOption("universal")]
    return build_option


@root.config(release_route)
def release(whl_config=None, **others):
    wheel_config = configure_or_default(whl_config, wheel)
    yield wheel_config, depends_on_stage(root, ["build:wheel"])
    _release_wheel()
    env_config = get_config_from_stage(root, env)
    env_config.update(get_config_from_stage(root, create))
    version_number = get_config_from_stage(root, build)["version"]
    horst = get_horst()
    dist_folder = os.path.join(horst.project_path, "dist")
    if not path.exists(dist_folder):
        return
    package = list(filter(
        lambda file_folder: horst.package_name in file_folder and version_number in file_folder,
        os.listdir(dist_folder)
    ))
    if len(package) == 1:
        _test_environment(env_config, os.path.join(horst.project_path, "dist", package[0]))


@root.register(release_route / test_release / wheel_route, route="release/wheel")
def _release_wheel():
    return [Printer("Executed ReleaseStage")]


@root.register(release_route / test_release)
def _test_environment(env_config, package_file):
    release_tests = get_config_from_stage(root, test).get("release", {})
    if not release_tests:
        return []  # [NoOperation("no tests for release specified. Nothing to do here!")]

    test_dependencies = env_config["test"]
    py_interpreter = env_config["python"]

    tempdir = tempfile.mkdtemp()
    env_path = path.join(tempdir, ".envtest")
    return [
        CreateEnv(env_path, py_interpreter),
        UpdateEnv(env_path, test_dependencies),
        CopyTree("test_structure", 2),
        UpdateEnv(env_path, [package_file])
       # RunTest("release")
    ]


def discover_test_with_pytest(test_options):
    filter_opts = list(filter(lambda x: "-k" in x or "-m" in x, test_options))
    folder = test_options[-1]