from horst import *
from os import path


Horst(__file__)


dependencies(
    install=["click", "jinja2", "bumpversion", "pytest-cov", "pytest", "virtualenv"],
    test=[],
    build=[],
    # versions={
    #     "py27": ("singledispatch",)
    # },
    environment=virtualenv(
        {
            # "py27": {'executable': "python"},
            ".env": {'python': "python3", 'main': True},
        }
    )
)


package(
    name="horst",
    version="0.0.1",  # bumpversion(),
    description="Horst is a simple build-automation-tool for python packages",
    url=from_git_config("origin"),
)


test(
    unittest=pytest(
        exclude=[marked_as("slow")],  # [marked_as("slow"), named("horst2")],
        include=[],
        report=junit(path=path.join(".testresults", "results.xml"), prefix=""),
        coverage=pytest_coverage(
            report=["html", "term"],
        )
    ),
    slow=pytest(
        exclude=[not_marked_as("slow")],
        coverage=pytest_coverage(
            append=True,
            min=95
        )
    )
)

# check(
#    flake8=True,
#    mypy=True,
#    pychecker=True,
#    untitest=pytest(".", exclude="integration_test"),
#    coverage=coverage(minimal=80),
#)

#release(
#    {
#        "py36": wheel(plattform="ANY", pyversions=["py3"]),
#        "py27": wheel(plattform="ANY", pyversions=["py27"]),
#    }
#)