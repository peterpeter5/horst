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

