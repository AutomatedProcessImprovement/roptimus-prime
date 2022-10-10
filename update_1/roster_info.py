# from itertools import groupby
# import numpy as np
#
#
# class Roster:
#     """
#     | Roster represents a work schedule for all resources in a process.
#     | Parameters:   name -> Name of the roster
#     |               resource_map -> list/map of resources that participate in the process
#     |               time_var -> Either 15 or 30, representing the division of shift blocks
#     |               TODO max_plat
#     """
#
#     def __init__(self, name, resource_map, time_var, max_cap, max_shift_size,
#                  max_plat):
#         self.name = name
#         self.resources = resource_map
#         self.time_var = time_var
#         self.max_cap = max_cap
#         self.max_shift_size = max_shift_size
#         self.max_plat = max_plat
#
#         # Two time variables: 15-min or 30-min block, assuming a work day is from 9:00 until 17:00 (8 hrs or 480 min)
#         # If 15 -> total roster columns = 32 slots
#         # If 30 -> total roster columns = 16 slots
#
#         self.slots = int(480 / time_var)
#
#         self.roster = {"MONDAY":        [[0] * self.slots] * len(self.resources),
#                        "TUESDAY":       [[0] * self.slots] * len(self.resources),
#                        "WEDNESDAY":     [[0] * self.slots] * len(self.resources),
#                        "THURSDAY":      [[0] * self.slots] * len(self.resources),
#                        "FRIDAY":        [[0] * self.slots] * len(self.resources)}
#         print(self.roster)
#         # After roster is initialized, check the current roster of a resource and fill in values in roster
#         for i in range(len(self.resources)):
#             for j in self.resources[i].shifts:
#                 match j:
#                     case "MONDAY":
#                         self.roster[j][i] = self.resources[i].shifts[j][i]
#             # _res_roster = resource.shifts
#             # self.roster.append(_res_roster)
#
#     def verify_roster(self):
#         # Step 1: Check if each row of roster (resource timetable) is the same length
#         roster_it = iter(self.roster)
#         timetable_l = len(next(roster_it))
#         if not all(len(r_l) == timetable_l for r_l in roster_it):
#             raise ValueError('Failed to verify: not all rosters are of same length.')
#
#         # Step 2: Verify if resource timetables are conforming the given constraints
#         # 2.1: Max Cap
#         block_sum = 0
#         for i in self.roster:
#             block_sum += i.count(1)
#         if block_sum > self.max_cap:
#             raise ValueError("Failed to verify: Too many slots taken")
#         # 2.2 Max Shift Size
#         for i in range(len(self.roster)):
#             grouped_roster = [(k, sum(1 for i in g)) for k, g in groupby(self.roster[i])]
#             for j, k in grouped_roster:
#                 if k > self.max_shift_size and j == 1:
#                     print("error")
#                     raise ValueError(
#                         "Failed to verify: Resource {} has a shift longer than {}".format(self.resources[i].id,
#                                                                                           self.max_shift_size))
#         # 2.3 Max Plateau
#         for i in range(len(self.roster)):
#             # TODO, may need to refine the roster to contain lists per day and not one large concat of lists
#             grouped_roster = [(k, sum(1 for i in g)) for k, g in groupby(self.roster[i])]
#             for j, k in grouped_roster:
#                 print((j, k))
#             print("--")
#         return True
#         pass
#
#     def pretty_print_roster(self):
#         # TODO
#         pass
#
#     def print_matrix(self):
#         return np.matrix(self.roster)
#
#
# class Resource:
#     def __init__(self, pool_id, name):
#         self.cost_per_hour = 0
#         self.id = pool_id
#         self.name = name
#         self.shifts = {"MONDAY": [], "TUESDAY": [], "WEDNESDAY": [], "THURSDAY": [], "FRIDAY": []}
#
#     # Returns True if at least 1 time block is found in the array representing the day.
#     def is_working(self, day):
#         match day:
#             case "MONDAY":
#                 return 1 in self.shifts[day]
#             case "TUESDAY":
#                 return 1 in self.shifts[day]
#             case "WEDNESDAY":
#                 return 1 in self.shifts[day]
#             case "THURSDAY":
#                 return 1 in self.shifts[day]
#             case "FRIDAY":
#                 return 1 in self.shifts[day]
#             case _:
#                 raise NameError("Day not recognized")
#
#     def set_shifts(self, shifts):
#         self.shifts = shifts
#
#     def set_cost(self, increase_by):
#         self.cost_per_hour += increase_by
#
#     def get_total_cost(self):
#         return self.cost_per_hour / 3600
#
#     def clone(self):
#         new_pool = Resource(self.id, self.name)
#         new_pool.cost_per_hour = self.cost_per_hour
#
#     def update_roster(self, roster):
#         self.shifts = roster
#
#     def enable_one_slot(self, day, index):
#         self.shifts[index] = 1
#
#     def disable_one_slot(self, day, index):
#         self.shifts[day][index] = 0
#
#     def disable_all(self):
#         self.shifts = [0 if x == 1 else 0 for x in self.shifts]
#
#     def enable_all(self):
#         self.shifts = [1 if x == 0 else 1 for x in self.shifts]
#
#     def __eq__(self, other):
#         return self.id == other.id and self.name == other.name
#
#
# class Slot:
#     def __init__(self):
#         self.busy = False
#
#     def set_busy(self, used):
#         self.busy = used
#
#     def get_busy(self):
#         return self.busy
