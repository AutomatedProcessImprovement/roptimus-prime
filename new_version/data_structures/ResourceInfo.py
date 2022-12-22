import datetime
from itertools import groupby

import pandas as pd

from new_version.support_modules.helpers import datetime_range, sum_of_binary_ones, _calculate_shifts, \
    _get_consecutive_shift_lengths, \
    _bitmap_to_valid_structure


class Resource:
    def __init__(self, constraints_json, timetable_json, time_var):
        # Resource general information
        self.id = constraints_json['id'].replace('timetable', '')
        self.resource_name = constraints_json['id'].replace('timetable', '')
        self.time_var = time_var
        self.num_slots = int(60 / self.time_var)
        self.total_amount = 1
        self.cost_per_hour = 1
        self.custom_id = ""

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
        # _format = "%H:%M:%S.%f"
        _format = "%H:%M:%S"

        # Default 24hr, 1hr per slot list (NOT IN USE)
        # default_df = [0] * 24

        # Initialize numbers
        monday = 0
        tuesday = 0
        wednesday = 0
        thursday = 0
        friday = 0
        saturday = 0
        sunday = 0

        # Translate time intervals to bitmaps
        for timetable in timetable_json["time_periods"]:
            if (timetable['from']) == 'MONDAY':
                monday += datetime_range(datetime.datetime.strptime(timetable['beginTime'], _format),
                                         datetime.datetime.strptime(timetable['endTime'], _format),
                                         datetime.timedelta(minutes=self.time_var), 24 * self.num_slots)
            elif (timetable['from']) == "TUESDAY":
                tuesday += datetime_range(datetime.datetime.strptime(timetable['beginTime'], _format),
                                          datetime.datetime.strptime(timetable['endTime'], _format),
                                          datetime.timedelta(minutes=self.time_var), 24 * self.num_slots)
            elif (timetable['from']) == "WEDNESDAY":
                wednesday += datetime_range(datetime.datetime.strptime(timetable['beginTime'], _format),
                                            datetime.datetime.strptime(timetable['endTime'], _format),
                                            datetime.timedelta(minutes=self.time_var), 24 * self.num_slots)
            elif (timetable['from']) == "THURSDAY":
                thursday += datetime_range(datetime.datetime.strptime(timetable['beginTime'], _format),
                                           datetime.datetime.strptime(timetable['endTime'], _format),
                                           datetime.timedelta(minutes=self.time_var), 24 * self.num_slots)
            elif (timetable['from']) == "FRIDAY":
                friday += datetime_range(datetime.datetime.strptime(timetable['beginTime'], _format),
                                         datetime.datetime.strptime(timetable['endTime'], _format),
                                         datetime.timedelta(minutes=self.time_var), 24 * self.num_slots)
            elif (timetable['from']) == "SATURDAY":
                saturday += datetime_range(datetime.datetime.strptime(timetable['beginTime'], _format),
                                           datetime.datetime.strptime(timetable['endTime'], _format),
                                           datetime.timedelta(minutes=self.time_var), 24 * self.num_slots)
            elif (timetable['from']) == "SUNDAY":
                sunday += datetime_range(datetime.datetime.strptime(timetable['beginTime'], _format),
                                         datetime.datetime.strptime(timetable['endTime'], _format),
                                         datetime.timedelta(minutes=self.time_var), 24 * self.num_slots)

        # Set remaining cap of weekdays
        self.day_free_cap['monday'] -= sum_of_binary_ones(monday)
        self.day_free_cap['tuesday'] -= sum_of_binary_ones(tuesday)
        self.day_free_cap['wednesday'] -= sum_of_binary_ones(wednesday)
        self.day_free_cap['thursday'] -= sum_of_binary_ones(thursday)
        self.day_free_cap['friday'] -= sum_of_binary_ones(friday)
        self.day_free_cap['saturday'] -= sum_of_binary_ones(saturday)
        self.day_free_cap['sunday'] -= sum_of_binary_ones(sunday)
        self.day_free_cap['total'] -= sum_of_binary_ones(monday) + sum_of_binary_ones(tuesday) \
                                      + sum_of_binary_ones(wednesday) + sum_of_binary_ones(thursday) \
                                      + sum_of_binary_ones(friday) + sum_of_binary_ones(saturday) \
                                      + sum_of_binary_ones(sunday)

        # Set remaining shifts of weekdays
        self.remaining_shifts['monday'] -= _calculate_shifts(monday)
        self.remaining_shifts['tuesday'] -= _calculate_shifts(tuesday)
        self.remaining_shifts['wednesday'] -= _calculate_shifts(wednesday)
        self.remaining_shifts['thursday'] -= _calculate_shifts(thursday)
        self.remaining_shifts['friday'] -= _calculate_shifts(friday)
        self.remaining_shifts['saturday'] -= _calculate_shifts(saturday)
        self.remaining_shifts['sunday'] -= _calculate_shifts(sunday)
        self.remaining_shifts['total'] -= _calculate_shifts(monday) + _calculate_shifts(tuesday) \
                                          + _calculate_shifts(wednesday) + _calculate_shifts(thursday) \
                                          + _calculate_shifts(friday) + _calculate_shifts(saturday) \
                                          + _calculate_shifts(sunday)

        # Set DF columns values.
        self.shifts['resource_id'] = [self.id]
        self.shifts['monday'] = monday
        self.shifts['tuesday'] = tuesday
        self.shifts['wednesday'] = wednesday
        self.shifts['thursday'] = thursday
        self.shifts['friday'] = friday
        self.shifts['saturday'] = saturday
        self.shifts['sunday'] = sunday

        self.custom_id = str([monday, tuesday, wednesday, thursday, friday, saturday, sunday])

    def get_total_cost(self):
        # Reduced to cost per second.
        return self.cost_per_hour / 3600

    def set_bpm_resource_name(self, name):
        self.bpm_resource_name = name

    def get_bpm_resource_name(self):
        return self.bpm_resource_name

    def set_bpm_resource_id(self, id):
        self.bpm_resource_id = id

    def get_bpm_resource_id(self):
        return self.bpm_resource_id

    # Getter for remaining cap of each day OR for one single day
    def get_free_cap(self, day=None):
        if day is not None:
            if type(day) == list:
                res = {}
                for d in day:
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
        changeable = self.never_work_masks[mask] ^ self.always_work_masks[mask]
        return changeable
        # for j, k in zip(self.never_work_masks[mask], self.always_work_masks[mask]):
        #     if j == 1:
        #         changeable.append(0)
        #     if k == 1:
        #         changeable.append(0)
        #     if j == 0 and k == 0:
        #         changeable.append(1)

    # Verify always_work_mask and never_work_mask
    def verify_masks(self, day=None):
        if day is None:
            for i in self.always_work_masks:
                return self.verify_masks(i)
        else:
            if not self.never_work_masks[day] | self.always_work_masks[day] == self.never_work_masks[day] ^ \
                   self.always_work_masks[day]:
                # print("ERR: Overlap in masks: {}".format(day))
                return False
            else:
                # Verify that the shifts are also conform the masks
                if self.never_work_masks[day] & self.shifts[day][0] == 0 and self.always_work_masks[day] & \
                        self.shifts[day][0] == self.always_work_masks[day]:
                    # print("Valid masks: {} & timetable valid under masks".format(day))
                    return True
                else:
                    # print("Conflict between masks and timetables.")
                    return False

            # for j, k in zip(self.never_work_masks[i], self.always_work_masks[i]):
            #     if k == j and k == 1:
            #         print("ERR: Overlap in masks: {}".format(i))
            # print("Valid masks: {}".format(i))

    # Verify global constraints
    # TODO when throw errors are implemented, remove else statements and write guardian statements
    def verify_global_constraints(self):
        shifts = self.shifts[['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']]
        sum_of_week = 0
        sum_of_shifts_week = 0
        for day in shifts:
            sum_of_day = sum_of_binary_ones(self.shifts[day][0])
            sum_of_week += sum_of_day

            if sum_of_day > self.max_daily_cap:
                # print("ERR: Max daily cap superseded on {}".format(day))
                return False
            else:
                self.set_free_cap(day, self.max_daily_cap - sum_of_day)

            shifts_of_day = _calculate_shifts(self.shifts[day][0])
            sum_of_shifts_week += shifts_of_day

            for _, tup in enumerate(_get_consecutive_shift_lengths(self.shifts[day][0])):
                if tup[0] == 1 and tup[1] > self.max_consecutive_cap:
                    # print("Err: Max daily shift size surpassed on {}".format(day))
                    return False

            if shifts_of_day > self.max_shifts_day:
                # print("Err: Max daily shifts surpassed on {}".format(day))
                return False
            else:
                self.set_weekly_shifts_remaining(day, self.max_shifts_day - shifts_of_day)

        if sum_of_week > self.max_weekly_cap:
            # print("ERR: Max weekly cap superseded for {}".format(self.id))
            return False
        else:
            self.set_free_cap('total', self.max_weekly_cap - sum_of_week)

        if sum_of_shifts_week > self.max_shifts_week:
            # print("ERR: Max weekly shifts superseded")
            return False
        return True

    def verify_timetable(self, day=None):
        if not self.is_human:
            return False
        if day is None:
            return self.verify_masks() & self.verify_global_constraints()
        else:
            return self.verify_masks(day) & self.verify_global_constraints()

    # --------------------START OF UPDATE METHODS-------------------------
    # The following methods all update / replace the shifts of a resource.
    # After updating the roster, the verify_timetable() method is called
    # TODO Check masks
    def set_shifts(self, shifts, day=None):
        if day is not None:
            self.shifts[day] = shifts
        else:
            for i in shifts:
                self.set_shifts(shifts[i], day=i)
        # self.verify_timetable()
        return self.shifts

    def set_custom_id(self):
        # new_uuid = str(uuid.uuid4())
        shifts = \
        self.shifts[['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']].values.tolist()[0]
        self.custom_id = shifts
        # self.custom_id = new_uuid

        # self.custom_id = str(sum(shifts))

    # def enable_shift(self, day, index):
    #     self.shifts[day].values[0][index] = 1
    #     self.day_free_cap[day] -= 1
    #     self.verify_timetable()
    #
    # def disable_shift(self, day, index):
    #     self.shifts[day].values[0][index] = 0
    #     self.day_free_cap[day] += 1
    #     self.verify_timetable()

    # def disable_day(self, day):
    #     self.shifts[day].values[0] = [0 if x == 1 else 0 for x in self.shifts[day].values[0]]
    #     self.day_free_cap[day] = sum(self.shifts[day].values[1])
    #     self.verify_timetable()
    #
    # def enable_day(self, day):
    #     self.shifts[day].values[0] = [1 if x == 0 else 1 for x in self.shifts[day].values[0]]
    #     self.day_free_cap[day] = sum(self.shifts[day].values[1])
    #     self.verify_timetable()

    # --------------------END OF UPDATE METHODS--------------------------

    # Compare two resources with each other
    def __eq__(self, other):
        return self.id == other.id  # and self.resource_name == other.resource_name

    # Write Resource object to a dict for easy conversion to JSON
    # TODO Rewrite bits instead of lists
    def to_dict(self):
        resource_calendar = {'id': self.id + "timetable", 'name': self.id + "timetable", 'time_periods': []}

        roster_df = self.shifts[['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']]
        for name, data in roster_df.iteritems():
            row = data.values[0]

            # Since 24hr blocks, a day always starts at 00:00:00
            start_of_day = datetime.datetime(hour=0, minute=0, year=1900, day=1, month=1)

            # Convert binary number to bitmap
            current_time = start_of_day
            bitmap = _bitmap_to_valid_structure(row, self.num_slots)
            grouped = [(key, len(list(group))) for key, group in groupby(bitmap)]

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
