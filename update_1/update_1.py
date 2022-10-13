import datetime, time
from itertools import groupby

import pandas as pd

import json


# TODO
#   Additional constraints: start_time_of_day, end_time_of_day | working_hours_in_day, resource_specific_hours_limit
#   RosterManager with functionalities:
#       - How much capacity is still available?
#       - How much capacity is still available on a certain day?
#       - How much capacity is still available for a certain resource?
#       - How much capacity is still available for a certain task? -> Requires additional module tracking which resources can perform which tasks
#   Initial HC algo / NSGA?
#   Add saturday/sunday to roster + change to 24hr schedules


def datetime_range(start, end, delta, df):
    _format = "%H:%M:%S"
    start_of_day = datetime.datetime.strptime('00:00:00', _format)
    end_of_day = datetime.datetime.strptime('23:59:59', _format)
    result = df

    current = start_of_day

    for j in range(len(df)):
        if start <= current < end:
            result[j] = 1
        current += delta
    return result


class Roster:

    """
    Roster represents the timetables of all resources in a dataframe.
        :parameter: roster_name -> Name for the roster
        :parameter: resource_map -> Map containing all resources active in the process
        :parameter: start_time_of_day -> Time when the business "opens"
        :parameter: end_time_of_day OR hours_in_day -> Time when business "closes" (Overtime not included)
        :parameter: time_variable -> Time is divided into blocks of how many minutes

    """

    def __init__(self, roster_name, resource_map, time_variable, hours_in_day, max_cap, max_shift_size,
                 max_shift_blocks):
        self.roster_name = roster_name
        self.resources = resource_map
        self.shift_block = time_variable
        self.max_cap = max_cap
        self.max_shift_size = max_shift_size
        self.max_shift_blocks = max_shift_blocks

        self.num_slots = int((hours_in_day * 60) / self.shift_block)

        self.roster = pd.DataFrame(columns=["resource_id", "resource_name",
                                            "monday", "tuesday",
                                            "wednesday", "thursday", "friday"])

        for resource in self.resources:
            self.roster = pd.concat([self.roster, resource.shifts], ignore_index=True)

    def verify_roster(self):
        roster = self.roster
        cap_sum = 0
        for idx, row in roster.iterrows():
            row = row[["monday", "tuesday", "wednesday", "thursday", "friday"]]
            for name, df in row.iteritems():
                cap_sum += df.count(1)
        if cap_sum > self.max_cap:
            print("Err: Max capacity surpassed")
        else:
            print("Max_cap ok")
        for idx, row in roster.iterrows():
            row = row[["monday", "tuesday", "wednesday", "thursday", "friday"]]
            for val in row:
                grouped = [(k, len(list(v))) for k, v in groupby(val)]
                for _, tup in enumerate(grouped):
                    if tup[0] == 1 and tup[1] > self.max_shift_size:
                        print("Err: Max shift size surpassed")

        for idx, row in roster.iterrows():
            row = row[["monday", "tuesday", "wednesday", "thursday", "friday"]]
            for val in row:
                grouped = [(k, len(list(v))) for k, v in groupby(val)]
                if len(grouped) > self.max_shift_blocks * 2:
                    print("Err: Max amount of shifts per day surpassed")

    def print_roster(self):
        return self.roster.to_string()

    def to_json(self):
        # json_string = json.dumps([ob.to_dict() for ob in self.resources], indent=4)

        return [ob.to_dict() for ob in self.resources]


class Resource:
    def __init__(self, resource_json, time_var, hours_in_day, never_work_mask=[], always_work_mask=[],
                 work_day_start=None, work_day_end=None):

        """
        Resource represents a participant in the process
        :parameter never_work_mask -> When is the resource never allowed to work. Ex. [[11111000000], [111100001111], [111111110000], ...]
        :parameter always_work_mask -> When is the resource always working. Ex. [[0000011100], [00001100110000], [0011000111100], ...]
        :parameter resource_json:
        :parameter time_var ->
        :parameter hours_in_day:
        :parameter work_day_start
        :parameter work_day_end
        """
        self.resource_id = resource_json["id"]
        self.resource_name = resource_json["name"]
        self.num_slots = int(60 / time_var)
        self.time_var = time_var
        self.work_day_start = work_day_start
        self.work_day_end = work_day_end

        self.shifts = pd.DataFrame(columns=["resource_name",
                                            "monday", "tuesday",
                                            "wednesday", "thursday", "friday", "saturday", "sunday"])

        _format = "%H:%M:%S"
        self.shifts['resource_id'] = [resource_json['id']]
        self.shifts['resource_name'] = [resource_json['name']]


        # TODO Reformat df creation to support 24 hr calendar slots
        # Default 24hr, 1hr per slot list
        default_df = [0]*24

        monday_df = default_df * self.num_slots
        tuesday_df = default_df * self.num_slots
        wednesday_df = default_df * self.num_slots
        thursday_df = default_df * self.num_slots
        friday_df = default_df * self.num_slots
        saturday_df = default_df * self.num_slots
        sunday_df = default_df * self.num_slots



        # monday_df = [0] * self.num_slots
        # tuesday_df = [0] * self.num_slots
        # wednesday_df = [0] * self.num_slots
        # thursday_df = [0] * self.num_slots
        # friday_df = [0] * self.num_slots
        for timetable in resource_json["time_periods"]:
            match timetable['from']:
                case "MONDAY":
                    monday_df = datetime_range(datetime.datetime.strptime(timetable['beginTime'], _format),
                                               datetime.datetime.strptime(timetable['endTime'], _format),
                                               datetime.timedelta(minutes=30), monday_df)
                case "TUESDAY":
                    tuesday_df = datetime_range(datetime.datetime.strptime(timetable['beginTime'], _format),
                                                datetime.datetime.strptime(timetable['endTime'], _format),
                                                datetime.timedelta(minutes=30), tuesday_df)
                case "WEDNESDAY":
                    wednesday_df = datetime_range(datetime.datetime.strptime(timetable['beginTime'], _format),
                                                  datetime.datetime.strptime(timetable['endTime'], _format),
                                                  datetime.timedelta(minutes=30), wednesday_df)
                case "THURSDAY":
                    thursday_df = datetime_range(datetime.datetime.strptime(timetable['beginTime'], _format),
                                                 datetime.datetime.strptime(timetable['endTime'], _format),
                                                 datetime.timedelta(minutes=30), thursday_df)
                case "FRIDAY":
                    friday_df = datetime_range(datetime.datetime.strptime(timetable['beginTime'], _format),
                                               datetime.datetime.strptime(timetable['endTime'], _format),
                                               datetime.timedelta(minutes=30), friday_df)
                case "SATURDAY":
                    saturday_df = datetime_range(datetime.datetime.strptime(timetable['beginTime'], _format),
                                               datetime.datetime.strptime(timetable['endTime'], _format),
                                               datetime.timedelta(minutes=30), saturday_df)
                case "SUNDAY":
                    sunday_df = datetime_range(datetime.datetime.strptime(timetable['beginTime'], _format),
                                               datetime.datetime.strptime(timetable['endTime'], _format),
                                               datetime.timedelta(minutes=30), sunday_df)

        self.shifts['monday'] = [monday_df]
        self.shifts['tuesday'] = [tuesday_df]
        self.shifts['wednesday'] = [wednesday_df]
        self.shifts['thursday'] = [thursday_df]
        self.shifts['friday'] = [friday_df]
        self.shifts['saturday'] = [saturday_df]
        self.shifts['sunday'] = [sunday_df]

    def enable_shift(self, day, index):
        self.shifts[day].values[0][index] = 1

    def disable_shift(self, day, index):
        self.shifts[day].values[0][index] = 0

    def disable_day(self, day):

        self.shifts[day].values[0] = [0 if x == 1 else 0 for x in self.shifts[day].values[0]]

    def enable_day(self, day):
        self.shifts[day].values[0] = [1 if x == 0 else 1 for x in self.shifts[day].values[0]]

    def __eq__(self, other):
        return self.resource_id == other.resource_id and self.resource_name == other.resource_name

    def to_dict(self):
        resource_calendar = {'id': self.resource_id, 'name': self.resource_name, 'time_periods': []}

        roster_df = self.shifts[['monday', 'tuesday', 'wednesday', 'thursday', 'friday']]

        for name, data in roster_df.iteritems():
            row = data.values[0]
            # Convert list to string values
            start_of_day = datetime.datetime(hour=9, minute=0, year=1900, day=1, month=1)
            current_time = datetime.datetime(hour=9, minute=0, year=1900, day=1, month=1)

            grouped = [(key, len(list(group))) for key, group in groupby(row)]

            for block in grouped:
                key, val = block
                if key == 1:
                    t_block = {
                        'from': str(name).upper(),
                        'to': str(name).upper(),
                    }
                    shift_start = current_time
                    shift_end = shift_start + (datetime.timedelta(minutes=self.time_var) * val)
                    t_block['beginTime'] = shift_start.time().strftime("%H:%M:%S")
                    t_block['endTime'] = shift_end.time().strftime("%H:%M:%S")
                    # Stuff to JSON
                    current_time = shift_end
                    resource_calendar['time_periods'].append(t_block)
                if key == 0:
                    block_start = current_time
                    block_end = block_start + (datetime.timedelta(minutes=self.time_var) * val)
                    current_time = block_end

        return resource_calendar
