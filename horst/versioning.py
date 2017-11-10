from os import path
from horst import get_project_path
from horst.effects import CreateFile, UpdateFile, RunCommand
from jinja2 import Template


_here = path.dirname(__file__)


class CreateBumpConfig(CreateFile):
    pass


class UpdateBumpConfig(UpdateFile):
    def __init__(self, files, args):
        super(UpdateBumpConfig, self).__init__(files, args)


class RunBumpVersion(RunCommand):
    def __init__(self):
        super(RunBumpVersion, self).__init__("bumpversion", "")


def _bump_version_config_exists(project):
    return path.exists(path.join(project, ".bumpversion.cfg"))


def bumpversion(files=None, git=True, tag=True):
    project = get_project_path()
    tasks = []
    if files is None:
        files = ["setup.py"]
    if not _bump_version_config_exists(project):
        bumpconfig_path = path.join(project, ".bumpversion.cfg")
        content = _render_int_bump_config(files, git, tag)
        tasks.append(CreateBumpConfig(bumpconfig_path, content))
    tasks.append(UpdateBumpConfig(files, ""))
    tasks.append(RunBumpVersion())
    return tasks


def _render_int_bump_config(files, git, tag):

    with open(path.join(_here, 'templates', 'bumpversion.template')) as template_content:
        template = Template(template_content.read(),
                            trim_blocks=True, lstrip_blocks=True)
        return template.render(files=files, commit=git, tag=tag)
