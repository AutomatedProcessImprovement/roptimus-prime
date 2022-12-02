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
    "production": {"bpmn": "./production/Production.bpmn",
                   "timetable": "./production/sim_json.json",
                   "constraints_out": "./production/constraints.json"},
    "purchasing_example": {"bpmn": "./purchasing_example/PurchasingExample.bpmn",
                       "timetable": "./purchasing_example/purchasing_example.json",
                       "constraints_out": "./purchasing_example/constraints.json"}
}

for log in logs.values():
    generate(log['timetable'], log['constraints_out'])






