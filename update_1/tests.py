from shutil import copyfile
from support_modules.log_parser import extract_data_from_xes_event_log
import json

# Initialize Test Resources
from RosterManager import RosterManager
from ResourceInfo import Resource
from RosterInfo import Roster

new_experiment_logs = {0: 'credit_application_diff',
                       1: 'credit_application_undiff'}

temp_bpmn_file = '../input_files/temp_files/CopiedModel.bpmn'

prosimos_file_paths = {
    'credit_application_diff': [
        '../test_assets/credit_application_diff.bpmn',
        '../test_assets/credit_application_diff.json',
        '../test_assets/log_demo_filtered_opt.xes'
    ],
    'credit_application_undiff': [
        '../test_assets/credit_application_undiff.bpmn',
        '../test_assets/credit_application_undiff.json',
        '../test_assets/log_demo_filtered_opt.xes'
    ]
}

# r = (''.join(map(str, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])))
# print(r)
# print(bin(27520))
# print("---\n")

log_name = new_experiment_logs[0]
bpmn_path = prosimos_file_paths[log_name][0]
json_path = prosimos_file_paths[log_name][1]
xes_path = prosimos_file_paths[log_name][2]

copyfile(bpmn_path, temp_bpmn_file)

xes_log_info = extract_data_from_xes_event_log(xes_path)

# # TODO Extract information about resource timetables from JSON file
with open(json_path, 'r') as f:
    json_data = json.load(f)

resource_calendars = json_data["resource_calendars"]
resource_profiles = json_data["resource_profiles"]

rest_of_info = {
    'resource_profiles': json_data['resource_profiles'],
    'arrival_time_distribution': json_data['arrival_time_distribution'],
    'arrival_time_calendar': json_data['arrival_time_calendar'],
    'gateway_branching_probabilities': json_data['gateway_branching_probabilities'],
    'task_resource_distribution': json_data['task_resource_distribution'],
}
# ----
test_timetable = './credit_application_diff.json'
test_constraints = './constraints.json'

with open(test_constraints, 'r') as c_read:
    r1_constraints = json.load(c_read)

with open(test_timetable, 'r') as t_read:
    r1_timetable = json.load(t_read)

res_map = []

time_var = 30
hours_in_day = 8

# Fill resource map with Resource objects from json.
for i in r1_timetable['resource_calendars']:
    for j in r1_constraints['resources']:
        if i['id'] == j['id']:
            res_map.append(Resource(j, i, r1_constraints['time_var']))

roster = Roster("test_roster", res_map, r1_constraints['time_var'], hours_in_day, 300, 4, 2)
# roster.verify_roster()
print("---- RESOURCE TESTS---")
print(res_map[0].get_changeable_bits())
print(res_map[0].get_free_cap())
print(res_map[0].get_weekly_shifts_remaining())
print(res_map[0].get_free_cap('monday'))
print(res_map[0].get_free_cap(['monday', 'tuesday']))
print(res_map[0].get_weekly_shifts_remaining('monday'))
print(res_map[0].get_weekly_shifts_remaining(['monday', 'tuesday']))
# res_map[0].verify_masks()
res_map[0].verify_global_constraints()
print(res_map[0].to_dict())

print("---- ROSTER TESTS---")
print(roster.verify_roster())

print("---- ROSTER MANAGER TESTS ----")
rm = RosterManager(roster)
print(rm.get_remaining_cap_resource("RESOURCE1"))
print(rm.get_remaining_cap_resource("RESOURCE1", 'wednesday'))
print(rm.get_remaining_cap_resource("RESOURCE1", ['wednesday', 'thursday']))
print("")
print(rm.get_accessible_bits("RESOURCE1"))
print(rm.get_accessible_bits("RESOURCE1", 'thursday'))
print(rm.get_accessible_bits("RESOURCE1", ['wednesday', 'thursday']))

print("")
print(rm.get_total_remaining_cap_resource("RESOURCE1"))


test_new_shifts = {
            'monday': 27520,
            'tuesday': 0,
            'wednesday': 27520,
            'thursday': 0,
            'friday': 27520,
            'saturday': 0,
            'sunday': 0
}
rm.set_new_shifts_on_resource("RESOURCE2", 27520, "monday")
rm.set_new_shifts_on_resource("RESOURCE3", test_new_shifts)


rest_of_info['resource_calendars'] = roster.to_json()

with open("test_out.json", 'w') as out:
    out.write(json.dumps(rest_of_info, indent=4))

"""

roster takes json with calendar and a json with parameters given by the user
resource json iterates over and creates a list of resources
param json contains all the constraints given by the user
if the value is unchanged then result to defaulted values

each resource has some constraints
- amount of hours the resource can work in one week +
- never work mask +
- always work mask +
- max time the resource may work in one day +
- max time the resource may work consecutively in one day +
- max amount of shifts a resource may have in one day +
- max amount of shifts a resource may have in one week +
- is the resource a human or a system +

extra params:
- json containing the current hours
- minutes in which blocks are split +


"""
