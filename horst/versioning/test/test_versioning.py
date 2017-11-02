from horst import Horst
from horst.versioning import bumpversion, UpdateBumpConfig, CreateBumpConfig, RunBumpVersion, _render_int_bump_config
from os import path
import horst.versioning

Horst(__file__)
here = path.dirname(__file__)

def test_bumpversion_nothing_existing():
    tasks = list(map(lambda x: x.__class__, bumpversion()))
    expected_bump_conf_file = path.join(here, ".bumpversion.conf")
    assert tasks == [CreateBumpConfig, UpdateBumpConfig, RunBumpVersion]


def test_bumpversion_does_not_create_new_config_if_one_exists():
    horst.versioning._bump_version_config_exists = lambda x: True
    tasks = [x.__class__ for x in bumpversion()]
    assert tasks == [UpdateBumpConfig, RunBumpVersion]


def test_bumpconfig_init_rendering():
    text = _render_int_bump_config(["setup.py"], True, True)
    expected_text = """
[bumbversion]
current_version = 0.0.1
commit = True
tag = True

[bumpversion:file:setup.py]
""".lstrip()
    assert expected_text == text 
