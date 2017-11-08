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
    version=bumpversion(),
)


test(
    unittest=pytest(
        # folders="horst",
        exclude=[],  # [marked_as("slow"), named("horst2")],
        include=[],
        report=junit(path=path.join(".testresults", "results.xml"), prefix=""),
        coverage=pytest_coverage(),
        #coverage=pytest_coverage(
        #    folders="horst",
        #    report=["html", "term"],
        #    # min=96,
        #    config=None
        #),
    ),
    integration_test=[]
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