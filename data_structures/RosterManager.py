import json
import os
import tempfile
from typing import List

from data_structures.ResourceInfo import Resource
from data_structures.RosterInfo import Roster
from data_structures.timetable import ResourceCalendarsItem, TimetableType
from support_modules.file_manager import  TMP_FOLDER


class RosterManager:
    def __init__(self, name:str, time_table_path:str, constraints_path:str):
        self.roster = Roster(name, time_table_path, constraints_path)
        self.time_table_path: str = time_table_path
        self.blocks = int(self.roster.shift_block / 60)
        self.constraints_path = constraints_path
        
        self.intermediate_timetable_path = os.path.abspath(os.path.join(TMP_FOLDER, 'intermediate_timetable.json'))
        self.intermediate_constraints_path = os.path.abspath(os.path.join(TMP_FOLDER, 'intermediate_constraints.json'))


        """
        TODOS:
        
        RosterManager should be able to give the free bits for a certain resource on a certain day
        RosterManager should be able to give the remaining capacity for a certain resource
        """

    def get_all_res_masks(self):
        all_res = {}
        for resource in self.roster.resources:
            all_res[resource.resource_name] = self.get_res_mask(resource)
        return all_res

    def get_all_res_accessible_bits(self):
        all_res = {}
        for resource in self.roster.resources:
            all_res[resource.resource_name] = self.get_accessible_bits(resource.id)
        return all_res

    def get_res_mask(self, resource):
        out = {'always_work': self.turn_bit_into_list_for_others(resource.always_work_masks), 'never_work': self.turn_bit_into_list_for_others(resource.never_work_masks)}
        return out

    def get_all_resources(self):
        return self.roster.resources

    def get_all_resources_in_dict(self):
        res_dict: dict[str, Resource] = dict()
        for res in self.get_all_resources():
            res_dict[res.id] = res
        return res_dict

    def get_task_pools(self):
        return self.roster.get_task_pools()


    def turn_bin_list_into_proper_length_array(self, value):
        new_arr = [0] * 24 * self.blocks
        new_arr[len(new_arr) - len(value)::] = value
        return new_arr

    def turn_bit_into_list_for_others(self, value):
        res_dict = {}
        for key, entry in value.items():
            res = self.turn_bin_list_into_proper_length_array([int(x) for x in bin(entry)[2:]])
            res_arr = []
            for i,j in enumerate(res):
                if j == 1:
                    res_arr.append(i)
            res_dict[key] = res_arr

        return res_dict

    def turn_bit_into_list_for_accessible(self, value):
        res_dict = {}
        for key, entry in value.items():
            res = [int(x) for x in bin(entry)[2:]]
            res_arr = []
            for i,j in enumerate(res):
                if j == 0:
                    res_arr.append(i)
            res_dict[key] = res_arr

        return res_dict

    def get_remaining_cap_resource(self, res, day=None):
        roster = self.roster.resources
        res = res+"timetable"
        for i in roster:
            if i.id == res:
                if day is not None:
                    if type(day) == list:
                        return i.get_free_cap(day)
                    return i.get_free_cap(day)
                return i.get_free_cap()

    def get_total_remaining_cap_resource(self, res):
        roster = self.roster.resources
        res = res + "timetable"
        for i in roster:
            if i.id == res:
                return i.get_free_cap()['total']

    def get_accessible_bits(self, resource, day=None, as_list=True):
        roster = self.roster.resources
        resource = resource
        if as_list:
            for i in roster:
                if i.id == resource:
                    if day is not None:
                        return self.turn_bit_into_list_for_accessible(i.get_changeable_bits(day))
                    return self.turn_bit_into_list_for_accessible(i.get_changeable_bits())
        else:
            for i in roster:
                if i.id == resource:
                    if day is not None:
                        return i.get_changeable_bits(day)
                    return i.get_changeable_bits()

    def set_new_shifts_on_resource(self, resource, shifts, day=None):
        roster = self.roster.resources
        resource = resource + "timetable"
        for i in roster:
            if i.id == resource:
                return i.set_shifts(shifts, day)



    def to_json(self) -> List[ResourceCalendarsItem]:
        return self.roster.to_json()

    def update_roster(self, pool_info):
        for resource in pool_info.pools.values():
            r = self.roster.find_resource(resource.id)
            if r is not None:
                r.set_shifts(resource.shifts)
        self.write_to_file()

    def generateTimetableJson(self, existing_timetable: TimetableType):
         return {'resource_profiles': existing_timetable['resource_profiles'],
                        'arrival_time_distribution': existing_timetable['arrival_time_distribution'],
                        'arrival_time_calendar': existing_timetable['arrival_time_calendar'],
                        'gateway_branching_probabilities': existing_timetable['gateway_branching_probabilities'],
                        'task_resource_distribution': existing_timetable['task_resource_distribution'],
                        'event_distribution': existing_timetable['event_distribution'],
                        'resource_calendars': self.to_json()}

    def write_to_file(self):
        with open(self.time_table_path, 'r') as t_read:
            ttb:TimetableType = json.load(t_read)
        
        rest_of_info = self.generateTimetableJson(ttb)

        with open(self.time_table_path, 'w') as out:
            out.write(json.dumps(rest_of_info, indent=4))
        out.close()

        return self.time_table_path
