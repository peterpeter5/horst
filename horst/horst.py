import os


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Horst(metaclass=Singleton):

    def __init__(self, file_path):
        self.project_path = os.path.dirname(file_path)
        self.cycle = {'release': [], 'build': [], "test": [], "check": []}

    def register_release(self, commands):
        self.cycle['release'].append(commands)

    def get_tasks(self):
        return [stage for stage, cmds in self.cycle.items() if cmds]


def get_project_path():
    return Horst("").project_path


def get_horst():
    return Horst("")