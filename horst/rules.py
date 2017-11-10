from functools import wraps


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

        route = _Route(self)
        return route / other

    @property
    def tasks(self):
        return self._tasks[-1] if len(self._tasks) != 0 else self._tasks

    def register_tasks(self, tasks):
        self._tasks.append(tasks)

    def __str__(self):
        return self.name


class _Route:

    def __init__(self, node):
        self._chain = [node]

    def __truediv__(self, other):
        if not isinstance(other, _Stage):
            raise TypeError("division between %s and %s is not definined" % (
                self.__class__, other.__class__))
        self._chain.append(other)
        return self

    @property
    def tasks(self):
        return [stage.tasks for stage in self]

    def __iter__(self):
        return (a for a in self._chain)

    def __str__(self):
        return ":".join((stage.name for stage in self))

    def register_tasks(self, tasks):
        self._chain[-1].register_tasks(tasks)


class Engine:

    def __init__(self):
        self._config = {}
        self._stages = {}

    def config(self, stage):
        def _inner(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                config = func(*args, **kwargs)
                self._config[func.__name__] = config
                return config

            return wrapper
        return _inner

    def register(self, stages, route=None):
        def _inner(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                tasks = func(*args, **kwargs)
                stages.register_tasks(tasks)
                name = str(stages) if route is None else route.replace("/", ":")
                self._stages[name] = stages
                return list(tasks) if tasks is not None else None

            return wrapper

        return _inner

    def get_config_for(self, key):
        return self._config.get(key, dict())

    def get_stages(self):
        return self._stages


def configure_or_default(variable, default_config):
    default_config = default_config() if callable(default_config) else default_config
    return variable if variable is not None else default_config


class VirtualEnv(_Stage):
    pass


class TestingStage(_Stage):
    pass


class Build(_Stage):
    pass


root = Engine()
env = VirtualEnv("env")
create = VirtualEnv("create")
update = VirtualEnv("update")

test = TestingStage("test")
unittest = TestingStage("unittest")

build = Build("build")
create_setup = Build("create_setup")
update_setup = Build("update_setup")
run_setup = Build("build_wheel")
clean_up = Build("clean_up")
