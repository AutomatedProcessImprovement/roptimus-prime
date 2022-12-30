import copy
import json


def generate(timetable_path, constraints_path):
    output = {
        "time_var": 60,
        "max_cap": 9999999999,
        "max_shift_size": 8,
        "max_shift_blocks": 2,
        "hours_in_day": 2,
        "resources": []
    }

    local_constraints = {
        "id": "",
        "constraints": {
            "global_constraints": {
                "max_weekly_cap": 40,
                "max_daily_cap": 8,
                "max_consecutive_cap": 8,
                "max_shifts_day": 2,
                "max_shifts_week": 20,
                "is_human": True
            },
            "daily_start_times": {
                "monday": "00:00:00",
                "tuesday": "00:00:00",
                "wednesday": "00:00:00",
                "thursday": "00:00:00",
                "friday": "00:00:00",
                "saturday": "None",
                "sunday": "None"
            },
            "never_work_masks": {
                "monday": 16711695,
                "tuesday": 16711695,
                "wednesday": 16711695,
                "thursday": 16711695,
                "friday": 16711695,
                "saturday": 16777215,
                "sunday": 16777215
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

    with open(timetable_path, 'r') as timetable:
        ttb = json.load(timetable)
    # Making undiff resources -> diff resources by making separate timetables
    # Changing timetable values from "MONDAY-SUNDAY" to "MONDAY-MONDAY | TUESDAY-TUESDAY"
    _days_in_week = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
    resource_calendars = ttb['resource_calendars']
    new_resource_calendars = []

    new_resource_profiles = []
    calendars = {}
    for calendar in resource_calendars:
        time_periods = calendar['time_periods']
        for time_period in range(len(time_periods)):
            if time_periods[time_period]['from'] != time_periods[time_period]["to"]:
                begin_time = time_periods[time_period]["beginTime"]
                end_time = time_periods[time_period]["endTime"]
                # Collect days that we need to slice from all days
                days_to_slices = [_days_in_week.index(time_periods[time_period]['from']),
                                  _days_in_week.index(time_periods[time_period]['to'])]
                list_to_iterate = _days_in_week[days_to_slices[0]:days_to_slices[1] + 1]
                new_time_periods = []
                for day in list_to_iterate:
                    new_time_period = {
                        "from": day,
                        "to": day,
                        "beginTime": begin_time,
                        "endTime": end_time
                    }
                    new_time_periods.append(new_time_period)

                calendar[time_period] = new_time_periods
                calendars[calendar['id']] = calendar[time_period]
            # Save new calendar, and make x copies based on # of resources
    resource_profiles = ttb['resource_profiles']

    for rp in resource_profiles:
        rest_of_info = {
            "id": rp['id'],
            "name": rp['name'],
            "resource_list": []
        }
        for r in rp['resource_list']:
            cal = copy.deepcopy(calendars[r['calendar']])
            r['calendar'] = r['id'] + "timetable"

            new_cal = {
                "id": r['id'] + "timetable",
                "name": r['id'] + "timetable",
                "time_periods": cal
            }
            rest_of_info['resource_list'].append(r)
            # Write new calendar to list to prep for write
            new_resource_calendars.append(new_cal)

        new_resource_profiles.append(rest_of_info)

    print(new_resource_calendars)
    print(new_resource_profiles)

    rest_of_info = {'resource_profiles': new_resource_profiles,
                    'arrival_time_distribution': ttb['arrival_time_distribution'],
                    'arrival_time_calendar': ttb['arrival_time_calendar'],
                    'gateway_branching_probabilities': ttb['gateway_branching_probabilities'],
                    'task_resource_distribution':  ttb['task_resource_distribution'],
                    'event_distribution': {},
                    'resource_calendars': new_resource_calendars}

    with open(timetable_path, 'w') as out:
        out.write(json.dumps(rest_of_info, indent=4))


    # Collect all unique resources from resource profiles
    unique_res = []
    ids = []
    resource_profiles = ttb['resource_profiles']
    for rp in resource_profiles:
        resources = rp['resource_list']
        for resource in resources:
            if not resource['id'] in ids:
                ids.append(resource['id'])
                unique_res.append(resource)
    print("-- Differentiating resources in timetable ... --")

    print("-- Generating constraints from timetable --")
    print("-- Total unique resources found: " + str(len(unique_res)))
    for res in unique_res:
        constraints_clean = copy.deepcopy(local_constraints)
        constraints_clean['id'] = res['id'] + "timetable"
        if "system" in res['name'].lower():
            constraints_clean['constraints']['global_constraints']['is_human'] = False
            constraints_clean['constraints']['never_work_masks'] = {
                "monday": 0,
                "tuesday": 0,
                "wednesday": 0,
                "thursday": 0,
                "friday": 0,
                "saturday": 0,
                "sunday": 0
            }
        else:
            constraints_clean['constraints']['global_constraints']['is_human'] = True
        output['resources'].append(constraints_clean)

    with open(constraints_path, 'w') as write:
        write.write(json.dumps(output, indent=4))


logs = {
    "production": {"bpmn": "./production/model.bpmn",
                   "timetable": "./production/timetable.json",
                   "constraints_out": "./production/constraints.json"},
    "purchasing_example": {"bpmn": "./purchasing_example/PurchasingExample.bpmn",
                           "timetable": "./purchasing_example/purchasing_example.json",
                           "constraints_out": "./purchasing_example/constraints.json"}
}

for log in logs.values():
    generate(log['timetable'], log['constraints_out'])
