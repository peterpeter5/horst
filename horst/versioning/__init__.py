from os import path
from horst import get_project_path
from horst.effects import CreateFile, UpdateFile, RunCommand


class CreateBumpConfig(CreateFile):
    pass


class UpdateBumpConfig(UpdateFile):
    def __init__(self, files):
        self.files = files


class RunBumpVersion(RunCommand):
    pass


def _bump_version_config_exists(project):
    return path.exists(path.join(project, ".bumpversion.cfg"))


def bumpversion(files=None):
    project = get_project_path()
    tasks = []
    if files is None:
        files = ["setup.py"]
    if not _bump_version_config_exists(project):
        tasks.append(CreateBumpConfig())
    tasks.append(UpdateBumpConfig(files))
    tasks.append(RunBumpVersion())
    return tasks

