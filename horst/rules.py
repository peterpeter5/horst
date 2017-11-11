from functools import wraps, reduce
from itertools import chain


class _Stage:

    def __init__(self, name=None):
        self._chain = [self]
        self._tasks = []
        self._depends_on = None
        self._name = name
        self._transformer = lambda x: x

    @property
    def depends_on(self):
        return self._depends_on if not callable(self._depends_on) else self._depends_on()

    @property
    def pending(self):
        return False if self.depends_on is None else True

    @property
    def name(self):
        return self._name if self._name is not None else self.__class__.__name__

    def task_transformer(self, func):
        self._transformer = func

    def __truediv__(self, other):
        if isinstance(other, _Stage):
            route = _Route([self])
            return route / other
        elif isinstance(other, _Route):
            return reduce(lambda first, sec: first / sec, other.to_stages(), self)
        else:
            raise TypeError("division between %s and %s is not definined" % (
                self.__class__, other.__class__))

    @property
    def tasks(self):
        return tuple(
            self._transformer(task)
            for task in (self._tasks[-1] if len(self._tasks) != 0 else self._tasks)
        )

    def register_tasks(self, tasks):
        tasks = tasks if tasks is not None else []
        self._tasks.append(tuple(tasks))
        return self

    def register_depends_on(self, stage_fut):
        self._depends_on = stage_fut
        return self

    def __str__(self):
        return self.name


class _Route:

    def __init__(self, node):
        self._chain = node

    def __truediv__(self, other):
        if isinstance(other, _Stage):
            self._chain.append(other)
            return self
        elif isinstance(other, _Route):
            return reduce(lambda left, right: left / right, chain(self.to_stages(), other.to_stages()))
        else:
            raise TypeError("division between %s and %s is not definined" % (
                self.__class__, other.__class__))

    def __mod__(self, other):
        if isinstance(other, _RouteChain):
            return _RouteChain([self]) % other
        elif isinstance(other, _Route):
            return _RouteChain([self, other])
        else:
            raise TypeError("Only Routes can depend on each other")

    def task_transformer(self, func):
        for stage in self:
            stage.task_transformer(func)

    @property
    def tasks(self):
        return [stage.tasks for stage in self]

    def __iter__(self):
        return (a for a in self._chain)

    def __str__(self):
        return ":".join((stage.name for stage in self))

    def register_tasks(self, tasks):
        self._chain[-1].register_tasks(tasks)

    @property
    def pending(self):
        return self._chain[0].pending

    @property
    def depends_on(self):
        return self._chain[0].depends_on

    def to_stages(self):
        return (stage for stage in self._chain)

    def iter_stagename_task(self):
        stage_name_list = reduce(
            lambda old_stages, stage: old_stages + [
                (":".join([old_stages[-1][0], stage.name]), stage.tasks)
            ],
            self._chain[1:],
            [(self._chain[0].name, self._chain[0].tasks)]
        )
        return stage_name_list


class _RouteChain:

    def __init__(self, routes):
        self.routes = routes

    def __mod__(self, other):
        if isinstance(other, _RouteChain):
            return _RouteChain(self.routes + other.routes)
        elif isinstance(other, _Route):
            return _RouteChain(self.routes + [other])
        else:
            raise TypeError("Only Routes can depend on each other")

    def __str__(self):
        return str([str(route) for route in self.routes])

    def iter_stagename_task(self):
        chained_iter_stage_task = ((name, task) for route in self.routes for name, task in route.iter_stagename_task())
        return chained_iter_stage_task


class Engine:

    def __init__(self):
        self._config = {}
        self._stages = {}

    def config(self, stage):
        def _inner(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                config = func(*args, **kwargs)
                config, dependend = config
                self._config[func.__name__] = config
                stage.register_depends_on(dependend)
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


def depends_on_stage(root, path_list):
    def find_best_suitable_stage():
        stages = root.get_stages()
        for path in path_list:
            if path in stages:
                return stages[path]
        else:
            return []

    return find_best_suitable_stage


def finalize_stage(stage_route, task_transformation=lambda x: x):
    stage_route.task_transformer(task_transformation)
    if stage_route.pending:
        return finalize_stage(stage_route.depends_on, task_transformation) % stage_route
    else:
        return stage_route


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
