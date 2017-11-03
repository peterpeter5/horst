from horst import *
Horst(__file__)


dependencies(
    install=["jinja2", "bumpversion", "pytest-cov"],
    test=["pytest", "pytest-cov"],
    build=[],
    versions={
        "py27": ("singledispatch",)
    },
    environment=virtualenv(
        {
            # "py27": {'executable': "python"},
            ".env": {'python': "python3", 'main': True},
        }
    )
)


package(
    name="horst",
    version=bumpversion(),
)

check(
    flake8=True,
    mypy=True,
    pychecker=True,
    untitest=pytest(".", exclude="integration_test"),
    coverage=coverage(minimal=80),
)

release(
    {
        "py36": wheel(plattform="ANY", pyversions=["py3"]),
        "py27": wheel(plattform="ANY", pyversions=["py27"]),
    }
    
)