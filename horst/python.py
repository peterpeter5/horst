from horst import get_horst
from horst.effects import EffectBase, ErrorBase
import re

class Versioning(EffectBase):
    def __init__(self, commands):
        self.commands = commands


class WrongPythonInterpreterSpec(ErrorBase):


def package(name, version):
    horst = get_horst()
    horst.register_release(Versioning(version))


def python_version(py_name, dependencies=[]):
    if not re.match(r'^py[thon]+\d{,2}', py_name):
        return 
    return 

def environment(dependencies=[], python=)
