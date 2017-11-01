from horst import Horst
from horst.versioning import bumpversion, UpdateBumpConfig, CreateBumpConfig, RunBumpVersion
from os import path
import horst.versioning

Horst(__file__)
here = path.dirname(__file__)

def test_bumpversion_nothing_existing():
    tasks = bumpversion()
    expected_bump_conf_file = path.join(here, ".bumpversion.conf")
    assert tasks == [CreateBumpConfig(), UpdateBumpConfig(""), RunBumpVersion()]


def test_bumpversion_does_not_create_new_config_if_one_exists():
    horst.versioning._bump_version_config_exists = lambda x: True
    tasks = bumpversion()
    assert tasks == [UpdateBumpConfig(""), RunBumpVersion()]