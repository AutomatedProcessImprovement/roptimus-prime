from datetime import *
from shutil import copyfile
from pprint import pprint

import pandas as pd

from support_modules.log_parser import extract_data_from_xes_event_log
import json

# Initialize Test Resources
from update_1 import Roster, datetime_range, Resource

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


res_map = []

time_var = 30
hours_in_day = 8

# Fill resource map with Resource objects from json.
for i in resource_calendars:
    res_map.append(Resource(i, time_var, hours_in_day))

# initialize roster with resources.
roster = Roster("test_roster", res_map, time_var, hours_in_day, 300, 4, 2)

# roster.resources[0].enable_shift("monday", 5)
# roster.resources[0].disable_shift("monday", 0)
# roster.resources[0].disable_day("tuesday")
# roster.resources[0].enable_day("wednesday")

print(roster.resources[0].shifts.to_string())

rest_of_info['resource_calendars'] = roster.to_json()


with open("test_out.json", 'w') as out:
    out.write(json.dumps(rest_of_info, indent=4))
# TODO
#  Bit flips in individual resource's calendars
#  All to 0 and all to 1
#  Is any working on certain time of shifts?
#  Is resource working on that day?
#  If resource is updated, is df roster also updated?
#  Validation function for all criteria
#  MAX CAP -> sum of all slots must be less than a given number (max hours worked in total per week)
#  MAX Shift size -> Max length of concurrent 1's
#  MAX Shifts -> Max amount of plateaus -> # of shifts per day per resource
