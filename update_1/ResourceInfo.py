import datetime
from itertools import groupby

import pandas as pd

from helpers import datetime_range


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

        # Daily start times (NOT IN USE YET)
        self.daily_start_times = constraints_json['constraints']['daily_start_times']

        # Resource never work mask
        self.never_work_masks = constraints_json['constraints']['never_work_masks']
        # Resource always work mask
        self.always_work_masks = constraints_json['constraints']['always_work_masks']

        # Remaining bits that can be enabled for each day and total
        self.day_free_cap = {
            'total': self.max_weekly_cap,
            'monday': self.max_daily_cap,
            'tuesday': self.max_daily_cap,
            'wednesday': self.max_daily_cap,
            'thursday': self.max_daily_cap,
            'friday': self.max_daily_cap,
            'saturday': self.max_daily_cap,
            'sunday': self.max_daily_cap
        }
        # Remaining shifts that can be created for each day and total
        self.remaining_shifts = {
            'total': self.max_shifts_week,
            'monday': self.max_shifts_day,
            'tuesday': self.max_shifts_day,
            'wednesday': self.max_shifts_day,
            'thursday': self.max_shifts_day,
            'friday': self.max_shifts_day,
            'saturday': self.max_shifts_day,
            'sunday': self.max_shifts_day
        }

        # Define column names for DF
        self.shifts = pd.DataFrame(columns=["resource_id",
                                            "monday", "tuesday",
                                            "wednesday", "thursday", "friday", "saturday", "sunday"])

        # Format for timestamps
        _format = "%H:%M:%S"

        # Default 24hr, 1hr per slot list
        default_df = [0] * 24

        # Initialize lists
        monday_df = default_df * self.num_slots
        tuesday_df = default_df * self.num_slots
        wednesday_df = default_df * self.num_slots
        thursday_df = default_df * self.num_slots
        friday_df = default_df * self.num_slots
        saturday_df = default_df * self.num_slots
        sunday_df = default_df * self.num_slots

        # Translate time intervals to bitmaps
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
        # TODO What is never mask doesnt allow work on that day? -> return 0?
        self.day_free_cap['monday'] -= sum(monday_df)
        self.day_free_cap['tuesday'] -= sum(tuesday_df)
        self.day_free_cap['wednesday'] -= sum(wednesday_df)
        self.day_free_cap['thursday'] -= sum(thursday_df)
        self.day_free_cap['friday'] -= sum(friday_df)
        self.day_free_cap['saturday'] -= sum(saturday_df)
        self.day_free_cap['sunday'] -= sum(sunday_df)
        self.day_free_cap['total'] -= sum(monday_df) + sum(tuesday_df) + sum(wednesday_df) + sum(thursday_df) + sum(
            friday_df) + sum(saturday_df) + sum(sunday_df)

        # Set DF columns to lists.
        self.shifts['resource_id'] = [self.resource_id]
        self.shifts['monday'] = [monday_df]
        self.shifts['tuesday'] = [tuesday_df]
        self.shifts['wednesday'] = [wednesday_df]
        self.shifts['thursday'] = [thursday_df]
        self.shifts['friday'] = [friday_df]
        self.shifts['saturday'] = [saturday_df]
        self.shifts['sunday'] = [sunday_df]

    # Getter for remaining cap of each day OR for one single day
    def get_free_cap(self, day=None):
        if day is not None:
            if type(day) == list:
                res = {}
                for d in day:
                    print(d)
                    res[d] = self.day_free_cap[d]
                return res
            return self.day_free_cap[day]
        return self.day_free_cap

    def set_free_cap(self, day, cap):
        self.day_free_cap[day] = cap

    # Getter for remaining shifts of each day OR for one single day
    def get_weekly_shifts_remaining(self, day=None):
        if day is not None:
            if type(day) == list:
                res = {}
                for d in day:
                    res[d] = self.remaining_shifts[d]
                return res
            return self.remaining_shifts[day]
        return self.remaining_shifts

    def set_weekly_shifts_remaining(self, day, cap):
        self.remaining_shifts[day] = cap

    # Getter for bits that can be changed in bitmap
    def get_changeable_bits(self, day=None):
        res_dict = {}
        if day is not None:
            if type(day) == list:
                res = {}
                for d in day:
                    res[d] = self._make_changeable_bits(d)
                return res
            return self._make_changeable_bits(day)
        for mask in self.always_work_masks:
            result = self._make_changeable_bits(mask)
            res_dict[mask] = result
        return res_dict

    # Helper method, translating always_work_mask and never_work_mask into changeable_bits
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

    # Verify always_work_mask and never_work_mask
    def verify_masks(self):
        for i in self.always_work_masks:
            for j, k in zip(self.never_work_masks[i], self.always_work_masks[i]):
                if k == j and k == 1:
                    print("ERR: Overlap in masks: {}".format(i))
            print("Valid masks: {}".format(i))

    # Verify global constraints
    # TODO when throw errors are implemented, remove else statements and write guardian statements
    def verify_global_constraints(self):
        print(self.shifts)
        shifts = self.shifts[['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']]
        sum_of_week = 0
        sum_of_shifts_week = 0
        for day in shifts:
            sum_of_day = sum(shifts[day][0])
            sum_of_week += sum_of_day

            if sum_of_day > self.max_daily_cap:
                print("ERR: Max daily cap superseded")
            else:
                self.set_free_cap(day, self.max_daily_cap - sum_of_day)

            grouped = [(k, len(list(v))) for k, v in groupby(shifts[day][0])]
            shifts_of_day = int(len(grouped) / 2)
            sum_of_shifts_week += shifts_of_day

            for _, tup in enumerate(grouped):
                if tup[0] == 1 and tup[1] > self.max_consecutive_cap:
                    print("Err: Max daily shift size surpassed")

            if shifts_of_day > self.max_shifts_day:
                print("Err: Max daily shifts surpassed")
            else:
                self.set_weekly_shifts_remaining(day, self.max_shifts_day - shifts_of_day)

        if sum_of_week > self.max_weekly_cap:
            print("ERR: Max weekly cap superseded")
        else:
            self.set_free_cap('total', self.max_weekly_cap - sum_of_week)

        if sum_of_shifts_week > self.max_shifts_week:
            print("ERR: Max weekly shifts superseded")

    def verify_timetable(self):
        self.verify_masks()
        self.verify_global_constraints()

    # --------------------START OF UPDATE METHODS--------------------------
    # The following methods all update / replace the shifts of a resource.
    # After updating the roster, the verify_timetable() method is called
    def set_shifts(self, shifts, day=None):
        if day is not None:
            self.shifts[day][0] = shifts
        else:
            for i in shifts:
                self.set_shifts(shifts[i], day=i)
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

    # --------------------END OF UPDATE METHODS--------------------------

    # Compare two resources with each other
    def __eq__(self, other):
        return self.resource_id == other.resource_id  # and self.resource_name == other.resource_name

    # Write Resource object to a dict for easy conversion to JSON
    def to_dict(self):
        resource_calendar = {'id': self.resource_id, 'name': self.resource_id, 'time_periods': []}

        roster_df = self.shifts[['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']]

        for name, data in roster_df.iteritems():
            row = data.values[0]
            # Since 24hr blocks, a day always starts at 00:00:00
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

                    current_time = shift_end
                    resource_calendar['time_periods'].append(t_block)

                if key == 0:
                    block_start = current_time
                    block_end = block_start + (datetime.timedelta(minutes=self.time_var) * val)
                    current_time = block_end

        return resource_calendar
