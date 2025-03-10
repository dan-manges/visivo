from ..factories.model_factories import AlertFactory, TraceFactory, ProjectFactory
from visivo.models.trace import Trace
from visivo.testing.runner import Runner
from tests.support.utils import temp_folder
from visivo.commands.utils import create_file_database
from visivo.models.target import Target, TypeEnum as TargetTypeEnum


def test_TestQueryStringFactory_errors(capsys):
    data = {
        "name": "two_test_trace",
        "props": {
            "type": "scatter",
            "x": "query(x)",
            "y": "query(y)",
        },
        "model": {"sql": "select * from test_table"},
        "tests": [
            {"coordinate_exists": {"coordinates": {"x": 3, "y": 2}}},
            {"coordinate_exists": {"coordinates": {"x": 19, "y": 26}}},
        ],
    }
    trace = Trace(**data)
    trace2 = TraceFactory()

    project = ProjectFactory(traces=[trace, trace2], dashboards=[])
    output_dir = temp_folder()
    alert = AlertFactory()
    target = Target(
        name="target",
        database=f"{output_dir}/test.db",
        type=TargetTypeEnum.sqlite,
    )

    create_file_database(url=target.url(), output_dir=output_dir)
    Runner(
        traces=[trace, trace2],
        project=project,
        target=target,
        output_dir=output_dir,
        alerts=[alert],
    ).run()
    captured = capsys.readouterr()
    assert (
        "two_test_trace-coordinate_exists-2: coordinates x=19, y=26 were not found in any trace cohort"
        in captured.out
    )
    assert alert.called
