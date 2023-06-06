import pytest
import json
from data_structures.RosterInfo import Roster

TIMETABLE_JSON = "tests/assets/timetable.json"
CONSTRAINTS_JSON = "tests/assets/constraints.json"


@pytest.fixture
def test_roster_class():
    # with open(TIMETABLE_JSON) as f:
    #     timetable_json = json.load(f)
    #
    # with open(CONSTRAINTS_JSON) as f:
    #     constraints_json = json.load(f)

    roster = Roster("Test Roster", TIMETABLE_JSON, CONSTRAINTS_JSON)
    return roster


def test_get_task_pools(test_roster_class):
    task_pools = test_roster_class.get_task_pools()
    assert len(task_pools) == 2
    assert "sid-cd20077b-8a4e-4e7d-a03f-ab1f89d7bebb" in task_pools
    assert "sid-7582aa81-12ca-4fb1-9124-b29e1d788777" in task_pools


def test_find_resource(test_roster_class):
    resource = test_roster_class.find_resource("Entity1")
    assert resource is not None
    assert resource.id == "Entity1"


def test_print_roster(test_roster_class):
    roster_str = test_roster_class.print_roster()
    assert isinstance(roster_str, str)

