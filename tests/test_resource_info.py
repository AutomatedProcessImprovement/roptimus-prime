from datetime import datetime, timedelta

import pytest

from data_structures.ResourceInfo import Resource
from data_structures.RosterInfo import Roster

TIMETABLE_JSON = "tests/assets/timetable.json"
CONSTRAINTS_JSON = "tests/assets/constraints.json"


@pytest.fixture
def test_resource():
    timetable_json = {
        "time_periods": [
            {
                "from": "MONDAY",
                "beginTime": "08:00:00",
                "endTime": "16:00:00"
            },
            {
                "from": "TUESDAY",
                "beginTime": "08:00:00",
                "endTime": "16:00:00"
            },
            {
                "from": "WEDNESDAY",
                "beginTime": "08:00:00",
                "endTime": "16:00:00"
            }
        ]
    }
    constraints_json = {
        "id": "Entity1timetable",
        "constraints": {
            "global_constraints": {
                "max_weekly_cap": 40,
                "max_daily_cap": 8,
                "max_consecutive_cap": 8,
                "max_shifts_day": 24,
                "max_shifts_week": 20,
                "is_human": True
            },
            "daily_start_times": {
                "monday": "13:00:00",
                "tuesday": "13:00:00",
                "wednesday": "13:00:00",
                "thursday": "13:00:00",
                "friday": "13:00:00",
                "saturday": None,
                "sunday": None
            },
            "never_work_masks": {
                "monday": 8388609,
                "tuesday": 8388609,
                "wednesday": 8388609,
                "thursday": 8388609,
                "friday": 8388609,
                "saturday": 8388609,
                "sunday": 8388609
            },
            "always_work_masks": {
                "monday": 0,
                "tuesday": 0,
                "wednesday": 0,
                "thursday": 0,
                "friday": 0,
                "saturday": 0,
                "sunday": 0
            }
        }
    }
    time_var = 60  # assuming time_var is 60 minutes

    resource = Resource(constraints_json, timetable_json, time_var)
    return resource


def test_resource_initialization(test_resource):
    assert test_resource.id == 'Entity1'
    assert test_resource.resource_name == 'Entity1'
    assert test_resource.time_var == 60
    assert test_resource.num_slots == 1
    assert test_resource.total_amount == 1
    assert test_resource.cost_per_hour == 1
    assert test_resource.custom_id == str([test_resource.shifts["monday"].iloc[0],
                                           test_resource.shifts["tuesday"].iloc[0],
                                           test_resource.shifts["wednesday"].iloc[0],
                                           test_resource.shifts["thursday"].iloc[0],
                                           test_resource.shifts["friday"].iloc[0],
                                           test_resource.shifts["saturday"].iloc[0],
                                           test_resource.shifts["sunday"].iloc[0]])
    assert test_resource.max_weekly_cap == 40
    assert test_resource.max_daily_cap == 8
    assert test_resource.max_consecutive_cap == 8
    assert test_resource.max_shifts_day == 24
    assert test_resource.max_shifts_week == 20
    assert test_resource.is_human == True


def test_get_total_cost(test_resource):
    assert test_resource.get_total_cost() == 1


def test_set_bpm_resource_name(test_resource):
    test_resource.set_bpm_resource_name("Resource1")
    assert test_resource.get_bpm_resource_name() == "Resource1"


def test_set_bpm_resource_id(test_resource):
    test_resource.set_bpm_resource_id("12345")
    assert test_resource.get_bpm_resource_id() == "12345"


def test_get_free_cap(test_resource):
    assert test_resource.get_free_cap('monday') == 0
    assert test_resource.get_free_cap(['monday', 'tuesday']) == {'monday': 0, 'tuesday': 0}
    assert test_resource.get_free_cap() == {
        'total': 16, 'monday': 0, 'tuesday': 0, 'wednesday': 0, 'thursday': 8, 'friday': 8, 'saturday': 8, 'sunday': 8
    }


def test_set_free_cap(test_resource):
    test_resource.set_free_cap('monday', 10)
    assert test_resource.get_free_cap('monday') == 10


def test_get_weekly_shifts_remaining(test_resource):
    assert test_resource.get_weekly_shifts_remaining('monday') == 23
    assert test_resource.get_weekly_shifts_remaining(['monday', 'tuesday']) == {'monday': 23, 'tuesday': 23}
