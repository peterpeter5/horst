import os
from .rules import root  

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super(Singleton, cls).__call__(*args, **kwargs)
            cls._instances[cls] = instance
            instance.__meta__ = cls
        return cls._instances[cls]


class Horst(metaclass=Singleton):

    __meta__ = None

    def __init__(self, file_path):
        self.project_path = os.path.dirname(file_path)
        self.cycle = {'release': [], 'build': [], "test": [], "check": []}

    def register_release(self, commands):
        self.cycle['release'].append(commands)

    def get_commands(self):
        return list(root.get_stages().items())
        # return [stage for stage, cmds in self.cycle.items() if cmds]

    def _invalidate(self):
        self.__meta__._instances.pop(self.__class__)


def get_project_path():
    return Horst("").project_path


def get_horst():
    return Horst("")
