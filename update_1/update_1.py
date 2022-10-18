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

        self.roster = pd.DataFrame(columns=["resource_id",
                                            "monday", "tuesday",
                                            "wednesday", "thursday", "friday", 'saturday', 'sunday'])

        for resource in self.resources:
            self.roster = pd.concat([self.roster, resource.shifts], ignore_index=True)

    def verify_roster(self):
        for resource in self.resources:
            print("\nVerifying resource: {}\n--------".format(resource.resource_id))
            resource.verify_timetable()
        roster = self.roster
        cap_sum = 0
        for idx, row in roster.iterrows():
            row = row[["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]]
            for name, df in row.iteritems():
                cap_sum += df.count(1)
        if cap_sum > self.max_cap:
            print("Err: Max capacity surpassed")
        else:
            print("Max_cap ok")
        for idx, row in roster.iterrows():
            row = row[["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]]
            for val in row:
                grouped = [(k, len(list(v))) for k, v in groupby(val)]
                for _, tup in enumerate(grouped):
                    if tup[0] == 1 and tup[1] > self.max_shift_size:
                        print("Err: Max shift size surpassed")

        for idx, row in roster.iterrows():
            row = row[["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]]
            for val in row:
                grouped = [(k, len(list(v))) for k, v in groupby(val)]
                if len(grouped) > self.max_shift_blocks * 2:
                    print("Err: Max amount of shifts per day surpassed")

    def print_roster(self):
        return self.roster.to_string()

    def to_json(self):
        return [ob.to_dict() for ob in self.resources]


class Resource:
    def __init__(self, constraints_json, timetable_json, time_var):

        # Resource general information
        self.resource_id = constraints_json['id']
        self.time_var = time_var
        self.num_slots = int(60 / self.time_var)

        global_constraints = constraints_json['constraints']['global_constraints']
        # Resource global constraints
        self.max_weekly_cap = global_constraints['max_weekly_cap']
        self.max_daily_cap = global_constraints['max_daily_cap']
        self.max_consecutive_cap = global_constraints['max_consecutive_cap']
        self.max_shifts_day = global_constraints['max_shifts_day']
        self.max_shifts_week = global_constraints['max_shifts_week']
        self.is_human = global_constraints['is_human']

        # Daily start times
        self.daily_start_times = constraints_json['constraints']['daily_start_times']

        # Resource never work mask
        self.never_work_masks = constraints_json['constraints']['never_work_masks']
        # Resource always work mask
        self.always_work_masks = constraints_json['constraints']['always_work_masks']

        # Some stats for easy recall
        self.day_free_cap = {
            'monday': self.max_daily_cap,
            'tuesday': self.max_daily_cap,
            'wednesday': self.max_daily_cap,
            'thursday': self.max_daily_cap,
            'friday': self.max_daily_cap,
            'saturday': self.max_daily_cap,
            'sunday': self.max_daily_cap
        }

        # Define column names for DF
        self.shifts = pd.DataFrame(columns=["resource_id",
                                            "monday", "tuesday",
                                            "wednesday", "thursday", "friday", "saturday", "sunday"])

        # Format for timestamps
        _format = "%H:%M:%S"

        # Default 24hr, 1hr per slot list
        default_df = [0] * 24

        monday_df = default_df * self.num_slots
        tuesday_df = default_df * self.num_slots
        wednesday_df = default_df * self.num_slots
        thursday_df = default_df * self.num_slots
        friday_df = default_df * self.num_slots
        saturday_df = default_df * self.num_slots
        sunday_df = default_df * self.num_slots

        for timetable in timetable_json["time_periods"]:
            match timetable['from']:
                case "MONDAY":
                    monday_df = datetime_range(datetime.datetime.strptime(timetable['beginTime'], _format),
                                               datetime.datetime.strptime(timetable['endTime'], _format),
                                               datetime.timedelta(minutes=self.time_var), monday_df)
                case "TUESDAY":
                    tuesday_df = datetime_range(datetime.datetime.strptime(timetable['beginTime'], _format),
                                                datetime.datetime.strptime(timetable['endTime'], _format),
                                                datetime.timedelta(minutes=self.time_var), tuesday_df)
                case "WEDNESDAY":
                    wednesday_df = datetime_range(datetime.datetime.strptime(timetable['beginTime'], _format),
                                                  datetime.datetime.strptime(timetable['endTime'], _format),
                                                  datetime.timedelta(minutes=self.time_var), wednesday_df)
                case "THURSDAY":
                    thursday_df = datetime_range(datetime.datetime.strptime(timetable['beginTime'], _format),
                                                 datetime.datetime.strptime(timetable['endTime'], _format),
                                                 datetime.timedelta(minutes=self.time_var), thursday_df)
                case "FRIDAY":
                    friday_df = datetime_range(datetime.datetime.strptime(timetable['beginTime'], _format),
                                               datetime.datetime.strptime(timetable['endTime'], _format),
                                               datetime.timedelta(minutes=self.time_var), friday_df)
                case "SATURDAY":
                    saturday_df = datetime_range(datetime.datetime.strptime(timetable['beginTime'], _format),
                                                 datetime.datetime.strptime(timetable['endTime'], _format),
                                                 datetime.timedelta(minutes=self.time_var), saturday_df)
                case "SUNDAY":
                    sunday_df = datetime_range(datetime.datetime.strptime(timetable['beginTime'], _format),
                                               datetime.datetime.strptime(timetable['endTime'], _format),
                                               datetime.timedelta(minutes=self.time_var), sunday_df)
        # Set remaining cap of weekdays
        self.day_free_cap['monday'] -= sum(monday_df)
        self.day_free_cap['tuesday'] -= sum(tuesday_df)
        self.day_free_cap['wednesday'] -= sum(wednesday_df)
        self.day_free_cap['thursday'] -= sum(thursday_df)
        self.day_free_cap['friday'] -= sum(friday_df)
        self.day_free_cap['saturday'] -= sum(saturday_df)
        self.day_free_cap['sunday'] -= sum(sunday_df)

        # Set DF columns to lists.
        self.shifts['resource_id'] = [self.resource_id]
        self.shifts['monday'] = [monday_df]
        self.shifts['tuesday'] = [tuesday_df]
        self.shifts['wednesday'] = [wednesday_df]
        self.shifts['thursday'] = [thursday_df]
        self.shifts['friday'] = [friday_df]
        self.shifts['saturday'] = [saturday_df]
        self.shifts['sunday'] = [sunday_df]


    def get_free_cap(self, day=None):
        if day is not None:
            return self.day_free_cap[day]
        return self.day_free_cap

    def get_changeable_bits(self, day=None):
        res_dict = {}
        if day is None:
            for mask in self.always_work_masks:
                result = self._make_changeable_bits(mask)
                res_dict[mask] = result
        else:
            mask = self.always_work_masks[day]
            return self._make_changeable_bits(mask)
        return res_dict

    def _make_changeable_bits(self, mask):
        changeable = []
        for j, k in zip(self.never_work_masks[mask], self.always_work_masks[mask]):
            if j == 1:
                changeable.append(0)
            if k == 1:
                changeable.append(0)
            if j == 0 and k == 0:
                changeable.append(1)
        return changeable

    def verify_masks(self):
        # Verify masks
        for i in self.always_work_masks:
            for j, k in zip(self.never_work_masks[i], self.always_work_masks[i]):
                if k == j and k == 1:
                    print("ERR: Overlap in masks: {}".format(i))
            print("Valid masks: {}".format(i))

    def verify_global_constraints(self):

        # Verify global constraints
        shifts = self.shifts[['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']]
        sum_of_week = 0
        sum_of_shifts_week = 0
        for day in shifts:
            sum_of_day = sum(shifts[day][0])

            sum_of_week += sum_of_day
            if sum_of_day > self.max_daily_cap:
                print("ERR: Max daily cap superseded")

            grouped = [(k, len(list(v))) for k, v in groupby(shifts[day][0])]
            # print(grouped)
            shifts_of_day = int(len(grouped) / 2)
            sum_of_shifts_week += shifts_of_day
            for _, tup in enumerate(grouped):
                if tup[0] == 1 and tup[1] > self.max_consecutive_cap:
                    print("Err: Max daily shift size surpassed")

            if shifts_of_day > self.max_shifts_day:
                print("Err: Max daily shifts surpassed")

        if sum_of_week > self.max_weekly_cap:
            print("ERR: Max weekly cap superseded")
        if sum_of_shifts_week > self.max_shifts_week:
            print("ERR: Max weekly shifts superseded")

    def verify_timetable(self):
        self.verify_masks()
        self.verify_global_constraints()

    def set_shifts(self, shifts, day=None):
        if day is not None:
            self.shifts[day] = shifts
        else:
            self.shifts = shifts
        self.verify_timetable()

    def enable_shift(self, day, index):
        self.shifts[day].values[0][index] = 1
        self.day_free_cap[day] -= 1
        self.verify_timetable()

    def disable_shift(self, day, index):
        self.shifts[day].values[0][index] = 0
        self.day_free_cap[day] += 1
        self.verify_timetable()

    def disable_day(self, day):
        self.shifts[day].values[0] = [0 if x == 1 else 0 for x in self.shifts[day].values[0]]
        self.day_free_cap[day] = sum(self.shifts[day].values[1])
        self.verify_timetable()

    def enable_day(self, day):
        self.shifts[day].values[0] = [1 if x == 0 else 1 for x in self.shifts[day].values[0]]
        self.day_free_cap[day] = sum(self.shifts[day].values[1])
        self.verify_timetable()

    def __eq__(self, other):
        return self.resource_id == other.resource_id and self.resource_name == other.resource_name

    def to_dict(self):
        resource_calendar = {'id': self.resource_id, 'name': self.resource_id, 'time_periods': []}

        roster_df = self.shifts[['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']]

        for name, data in roster_df.iteritems():
            row = data.values[0]
            start_of_day = datetime.datetime(hour=0, minute=0, year=1900, day=1, month=1)

            # Convert list to string values
            current_time = start_of_day
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
