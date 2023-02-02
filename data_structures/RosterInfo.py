import json

import pandas as pd

from data_structures.ResourceInfo import Resource
from support_modules.helpers import sum_of_binary_ones


class Roster:
    """
    Roster represents the timetables of all resources in a dataframe.
        :parameter: roster_name -> Name for the roster
        :parameter: resource_map -> Map containing all resources active in the process
        :parameter: start_time_of_day -> Time when the business "opens"
        :parameter: end_time_of_day OR hours_in_day -> Time when business "closes" (Overtime not included)
        :parameter: time_variable -> Time is divided into blocks of how many minutes
        TODO: Replace print(ERR) lines with Error throws
    """

    def __init__(self, name, time_table, constraints):
        self.roster_name = name
        self.task_pools = dict()

        with open(time_table, 'r') as t_read:
            ttb = json.load(t_read)

        with open(constraints, 'r') as c_read:
            cons = json.load(c_read)

        resource_map = []


        for i in ttb['resource_calendars']:
            for j in cons['resources']:
                if i['id'] == j['id']:
                    resource_map.append(Resource(j, i, cons['time_var']))
        self.resources = resource_map
        self.shift_block = cons['time_var']
        self.max_cap = cons['max_cap']
        self.max_shift_size = cons['max_shift_size']
        self.max_shift_blocks = cons['max_shift_blocks']

        self.num_slots = int((cons['hours_in_day'] * 60) / self.shift_block)

        self.roster = pd.DataFrame(columns=["resource_id",
                                            "monday", "tuesday",
                                            "wednesday", "thursday", "friday", 'saturday', 'sunday'])

        for resource in self.resources:
            self.roster = pd.concat([self.roster, resource.shifts], ignore_index=True)

        for task in ttb['resource_profiles']:

            self.task_pools[task['id']] = \
                [resource for resource in task['resource_list']]

    def get_task_pools(self):
        return self.task_pools

    def find_resource(self, r_id):
        for resource in self.resources:
            if resource.id == r_id:
                return resource

    # def __init__(self, roster_name, resource_map, time_variable, hours_in_day, max_cap, max_shift_size,
    #              max_shift_blocks):
    #     self.roster_name = roster_name
    #     self.resources = resource_map
    #     self.shift_block = time_variable
    #     self.max_cap = max_cap
    #     self.max_shift_size = max_shift_size
    #     self.max_shift_blocks = max_shift_blocks
    #
    #     self.num_slots = int((hours_in_day * 60) / self.shift_block)
    #
    #     self.roster = pd.DataFrame(columns=["resource_id",
    #                                         "monday", "tuesday",
    #                                         "wednesday", "thursday", "friday", 'saturday', 'sunday'])
    #
    #     for resource in self.resources:
    #         self.roster = pd.concat([self.roster, resource.shifts], ignore_index=True)

    def verify_roster(self):
        for resource in self.resources:
            print("\nVerifying resource: {}\n--------".format(resource.id))
            resource.verify_timetable()
        roster = self.roster
        cap_sum = 0
        print("---- Resources validated----")
        for idx, row in roster.iterrows():
            row = row[["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]]
            for name, df in row.iteritems():
                cap_sum += sum_of_binary_ones(df)
        if cap_sum > self.max_cap:
            print("Err: Global resource max capacity surpassed")
        else:
            print("Max_cap ok")
        # for idx, row in roster.iterrows():
        #     row = row[["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]]
        #     for val in row:
        #         grouped = [(k, len(list(v))) for k, v in groupby(val)]
        #         for _, tup in enumerate(grouped):
        #             if tup[0] == 1 and tup[1] > self.max_shift_size:
        #                 print("Err: Max shift size surpassed")

        # for idx, row in roster.iterrows():
        #     row = row[["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]]
        #     for val in row:
        #         grouped = [(k, len(list(v))) for k, v in groupby(val)]
        #         if len(grouped) > self.max_shift_blocks * 2:
        #             print("Err: Max amount of shifts per day surpassed")

    def print_roster(self):
        return self.roster.to_string()

    def to_json(self):
        return [ob.to_dict() for ob in self.resources]
