from functools import wraps, reduce


class _Stage:

    def __init__(self, name=None):
        self._chain = [self]
        self._tasks = []
        self._name = name

    @property
    def name(self):
        return self._name if self._name is not None else self.__class__.__name__

    def __truediv__(self, other):
        if not isinstance(other, _Stage):
            raise TypeError("division between %s and %s is not definined" % (
                self.__class__, other.__class__))
        self._chain.append(other)
        return self

    @property
    def tasks(self):
        return [stage._tasks for stage in self]

    def __iter__(self):
        return(a for a in self._chain)

    def __str__(self):
        return ".".join((stage.name for stage in self))

    def register_tasks(self, tasks):
        self._chain[-1]._tasks = tasks


class Engine:

    def __init__(self):
        self._config = {}
        self._stages = {}

    def config(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            config = func(*args, **kwargs)
            self._config[func.__name__] = config
            return config

        return wrapper

    def register(self, stages):
        def _inner(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                tasks = func(*args, **kwargs)
                stages.register_tasks(tasks)
                self._stages[str(stages)] = stages.tasks
                return tasks

            return wrapper
        return _inner

    def get_config_for(self, key):
        return self._config.get(key, dict())


class VirtualEnv(_Stage):
    pass


root = Engine()
env = VirtualEnv()
create = VirtualEnv("create")
update = VirtualEnv("update")
