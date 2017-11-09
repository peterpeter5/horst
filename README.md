# HORST
(WIP: some of the described features here might not have been
implemented. Currently only linux is supported (espacially tested. This might change in the future)

## package-development made simple
Lets start with some code and a maybe-timeline of a package-development-process.

1. Have an idea and an name
    -> develop horst2

2. make a folder called horst2 and inside start a package horst2:
    -> horst2
        | - horst2
            | - __init__.py
3. make your first build.py
```python
from horst import *
Horst(__file__)
```
4. open a commandline
```
horst2 $ horst
>>>
Options:
  -d, --dry      DryRun nothing will be executed
  -v, --verbose  Output everything to cli
  --help         Show this message and exit.

Commands:
  env:create
  env:update
  test
  debug
```

5. Create a new virutalenv by:
```
$ horst env:create
```
Now you have a new virtualenv in your main-folder called ".env"

6. write some code and tests
7. run all test:
```
horst test
```



## what it is

horst is a build-automation-system. It aims to help python-developers
to get an more easy experience when it comes to building a package
and releasing it. For that horst tries to be as simple as possible
and does not invent anything new. Because of this horst depends on
many great libraries like:
    - pytest + plugins
    - bumpversion
    - flake8
    - virtualenv
    - ...

  ## what it is NOT

  1. small footprint: you NEVER want to have Horst as a production
  dependency! There are to many downstream dependencies from Horst

  2. a new build-system: unlike conda or others the main goal of horst is
  to provide a good "standard" - process for developing and releasing
  packages. Horst simply orchestreates other "standard" - tools

  3. The one true way to do it: At the moment Horst simply refelects
  what I believe is a good process. You may not agree with me, thats
  fine. Horst tries to rely on as many "pythonic" - conventions as
  possible, but it is opinioneted. There are ways to change Horst
  behaviour, but sometimes it may be easier to stick to the Horst-way

