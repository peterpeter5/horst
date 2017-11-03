from functools import wraps, reduce


class _Stage:

    def __init__(self):
        self._chain = [self]
        self._tasks = []

    def __truediv__(self, other):
        if not isinstance(other, _Stage):
            raise TypeError("division between %s and %s is not definined" % (self.__class__, other.__class__))
        self._chain.append(other)
        return self

    @property
    def tasks(self):
        return [stage._tasks for stage in self]

    def __iter__(self):
        return(a for a in self._chain)
    
    def __str__(self):
        return ".".join((stage.__class__.__name__ for stage in self))
    
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
        
        return wrapper

    def register(self, stages):
        def _inner(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                tasks = func(*args, **kwargs)
                stages.register_tasks(tasks)
                self._stages[str(stages)] = stages.tasks
            return wrapper
        return _inner