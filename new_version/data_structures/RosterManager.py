import json

from new_version.data_structures.RosterInfo import Roster


class RosterManager:
    def __init__(self, name, time_table, constraints):

        self.roster = Roster(name, time_table, constraints)
        self.time_table = time_table

        """
        TODOS:
        
        RosterManager should be able to give the free bits for a certain resource on a certain day
        RosterManager should be able to give the remaining capacity for a certain resource
        """

    def turn_bit_into_list(self, value):
        print(value)
        return ""

    def get_remaining_cap_resource(self, res, day=None, as_list=True):
        roster = self.roster.resources
        if as_list:
            for i in roster:
                if i.resource_id == res:
                    if day is not None:
                        if type(day) == list:
                            return self.turn_bit_into_list(i.get_free_cap(day))
                        return self.turn_bit_into_list(i.get_free_cap(day))
                    return self.turn_bit_into_list(i.get_free_cap())
        else:
            for i in roster:
                if i.resource_id == res:
                    if day is not None:
                        if type(day) == list:
                            return i.get_free_cap(day)
                        return i.get_free_cap(day)
                    return i.get_free_cap()

    def get_total_remaining_cap_resource(self, res):
        roster = self.roster.resources
        for i in roster:
            if i.resource_id == res:
                return i.get_free_cap()['total']

    def get_accessible_bits(self, resource, day=None, as_list=True):
        roster = self.roster.resources
        if as_list:
            for i in roster:
                if i.resource_id == resource:
                    if day is not None:
                        return self.turn_bit_into_list(i.get_changeable_bits(day))
                    return self.turn_bit_into_list(i.get_changeable_bits())
        else:
            for i in roster:
                if i.resource_id == resource:
                    if day is not None:
                        return i.get_changeable_bits(day)
                    return i.get_changeable_bits()

    def set_new_shifts_on_resource(self, resource, shifts, day=None):
        roster = self.roster.resources
        for i in roster:
            if i.resource_id == resource:
                return i.set_shifts(shifts, day)



    def to_json(self):
        return self.roster.to_json()

    def write_to_file(self):
        out_path = "./test_assets/timetable.json"

        with open(self.time_table, 'r') as t_read:
            ttb = json.load(t_read)

        rest_of_info = {'resource_profiles': ttb['resource_profiles'],
                        'arrival_time_distribution': ttb['arrival_time_distribution'],
                        'arrival_time_calendar': ttb['arrival_time_calendar'],
                        'gateway_branching_probabilities': ttb['gateway_branching_probabilities'],
                        'task_resource_distribution': ttb['task_resource_distribution'],
                        'resource_calendars': self.to_json()}

        with open(out_path, 'w') as out:
            out.write(json.dumps(rest_of_info, indent=4))
        out.close()

        return out_path
