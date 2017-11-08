import os
from .rules import root
import warnings


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

    def __init__(self, file_path, package_name=None, root_engine=root):
        self.root = root_engine
        self.project_path = os.path.dirname(file_path)
        _, folder_name = os.path.split(self.project_path)
        self.package_name = package_name if package_name is not None else folder_name
        self.cycle = {'release': [], 'build': [], "test": [], "check": []}

    @property
    def package_path(self):
        package_path = os.path.join(self.project_path, self.package_name)
        if not os.path.exists(package_path):
            warnings.warn(
                "your package-folder <%s> does not exists. Plase specify a correct one at horst" % package_path
            )
        return package_path

    def register_release(self, commands):
        self.cycle['release'].append(commands)

    def get_commands(self):
        return self.root.get_stages()
        # return [stage for stage, cmds in self.cycle.items() if cmds]

    def _invalidate(self):
        self.__meta__._instances.pop(self.__class__)

    def get_horst_state(self):
        return {
            'config': self.root._config,
            'stages': self.root._stages,
        }


def get_project_path():
    return Horst("").project_path


def get_horst():
    return Horst("")
