import copy
import json
import shutil
import sys
from shutil import copyfile
import time
import datetime
import random
from new_version.data_structures.pools_info import PoolInfo
from new_version.pareto_algorithms_and_metrics.pareto_metrics import AlgorithmResults
from new_version.support_modules.file_manager import save_stats_file, read_stats_file
from new_version.support_modules.helpers import _list_to_binary, _bitmap_to_valid_structure
from new_version.pareto_algorithms_and_metrics.iterations_handler import IterationHandler
from new_version.data_structures.RosterManager import RosterManager
import hashlib

temp_bpmn_file = './test_assets/CopiedModel.bpmn'


def hill_climb(log_name, bpmn_path, time_table, constraints, max_func_ev, non_opt_ratio, tot_simulations,
               is_tabu, with_mad, only_calendar):
    cost_type = 1

    # SETUP
    copyfile(bpmn_path, temp_bpmn_file)
    rm = RosterManager("DEFAULT_ROSTER2", time_table, constraints)

    starting_time = time.time()
    algorithm_name = 'tabu_srch' if is_tabu else 'hill_clmb'

    initial_pools_info = PoolInfo(rm.get_all_resources_in_dict(), rm.get_task_pools())
    it_handler = IterationHandler(log_name, initial_pools_info, tot_simulations, is_tabu, with_mad, rm)
    max_iterations_reached = True
    # max_resources = initial_pools_info.total_resoures

    iterations_count = [0]
    # Setup start clause

    while it_handler.solutions_count() < max_func_ev:
        if it_handler.pareto_update_distance >= non_opt_ratio * max_func_ev or not it_handler.has_next():
            max_iterations_reached = False
            break

        iteration_info = it_handler.next()
        solution_resolve_optimization(iteration_info, it_handler, iterations_count,
                                      only_calendar)

    save_stats_file(log_name,
                    algorithm_name + ('_with_mad' if with_mad else '_without_mad'),
                    it_handler.generated_solutions,
                    it_handler.solution_order,
                    iterations_count[0])

    print("MAX Number of Iterations Reached") if max_iterations_reached else print("NO Improvement Found")
    print("Algortithm %s Completed" % algorithm_name)
    print("Process Name: %s" % log_name)
    print("Total time (sec): ................ %s " % str(datetime.timedelta(seconds=(time.time() - starting_time))))
    print("Total Iterations Performed: ...... %d" % iterations_count[0])
    print("Total Solutions Explored: ........ %d" % len(it_handler.generated_solutions))
    execution_info = read_stats_file(log_name, algorithm_name + '_without_mad')
    alg_info = AlgorithmResults(execution_info, False)
    print("Discovered Pareto Size: .......... %d" % len(alg_info.pareto_front))
    print("---------------------------------------------------")


def resolve_remove_resources_in_process(iteration_info, iterations_handler, iterations_count, res_manager):
    pools_info, simulation_info, distance = iteration_info[0], iteration_info[1], iteration_info[2]
    if pools_info is None:
        return None
    iterations_count[0] += 1

    resources_to_optimize = {}
    # the first resource in pool_cost is the most expensive
    for pool in simulation_info.pools_info.pools:
        pool_cost = simulation_info.pools_info.pools[pool].cost_per_hour * simulation_info.available_time[pool]
        resources_to_optimize[pool] = pool_cost

    resources_to_optimize = sort_resource_by_cost(resources_to_optimize)

    for resource in resources_to_optimize:
        resource_to_optimize = resource
        # Collect for each trace, the information of which task was executed on which day
        tasks_of_resource = []
        for task in pools_info.task_pools:
            for res in pools_info.task_pools[task]:
                if res['id'] == resource_to_optimize:
                    tasks_of_resource.append(task)
        just_a_task_to_get_resource_info = tasks_of_resource[0]
        # for res in resource_to_optimize:
        actual_resource_info = pools_info.task_pools[just_a_task_to_get_resource_info]
        resource_copy = copy.deepcopy(actual_resource_info)
        if len(actual_resource_info) > 1:
            for res in resource_copy:
                ready_to_sim = resolve_remove_resource_json_information(res, res_manager)
                if ready_to_sim[0]:
                    new_res_manager = ready_to_sim[1]
                    iterations_handler.resource_manager = new_res_manager
                    iterations_handler.time_table_path = new_res_manager.time_table
                    new_pools_info = PoolInfo(new_res_manager.get_all_resources_in_dict(),
                                              new_res_manager.get_task_pools())
                    print("---")
                    print(new_res_manager.get_all_resources_in_dict())
                    print("---")
                    if _try_solution_new_resource(new_pools_info, iterations_handler, distance):
                        return True
                    else:
                        # Replace timetable and constraints with updated jsons. + reset resource_manager
                        print("sim w/ removed resource discarded - resetting timetables")
                        shutil.copyfile(res_manager.temp_timetable, res_manager.time_table)
                        shutil.copyfile(res_manager.temp_constraints, res_manager.constraints_json)

                        new_res_manager = RosterManager(res_manager.roster.roster_name, res_manager.time_table,
                                                        res_manager.constraints_json)
                        iterations_handler.resource_manager = new_res_manager
                        iterations_handler.time_table_path = new_res_manager.time_table

                else:
                    # Replace timetable and constraints with updated jsons.
                    print("Ready sim failed - resetting timetables")
                    shutil.copyfile(res_manager.temp_timetable, res_manager.time_table)
                    shutil.copyfile(res_manager.temp_constraints, res_manager.constraints_json)
    return False


def solution_resolve_optimization(iteration_info, iterations_handler, iterations_count,
                                  only_calendar):
    print("WT")
    s1 = solution_traces_sorting_by_waiting_times(iteration_info, iterations_handler, iterations_count,
                                                  iterations_handler.resource_manager)
    print("Cost")
    s2 = solution_traces_optimize_cost(iteration_info, iterations_handler, iterations_count, iterations_handler.resource_manager)
    print("IT")
    s3 = solution_traces_sorting_by_idle_times(iteration_info, iterations_handler, iterations_count, iterations_handler.resource_manager)

    if not only_calendar:
        # print("WT | Add")
        # s4 = resolve_add_resources_in_process(iteration_info, iterations_handler, iterations_count, iterations_handler.resource_manager)
        # print("Cost | Remove")
        # s4 = True
        # s5 = resolve_remove_resources_in_process(iteration_info, iterations_handler, iterations_count, iterations_handler.resource_manager)
        # return s1 or s2 or s3 or s4 or s5
        return s1 or s2 or s3
    # return s1
    return s1 or s2 or s3


def resolve_reschedule_resource_json_information(resource, roster_manager, task_to_improve, task_resource_occurences):
    # 0.1 !!! MAKE BACKUP OF CONSTRAINTS AND TIMETABLE
    shutil.copyfile(roster_manager.time_table, roster_manager.temp_timetable)
    shutil.copyfile(roster_manager.constraints_json, roster_manager.temp_constraints)

    # 1. Find resource and check his tasks
    tasks_resource_can_perform = resource['assigned_tasks']
    potential_to_be_removed = [task for task in tasks_resource_can_perform if task != task_to_improve]
    # 2. Count times resource performs certain task vs. total times task occurred.
    lowest_number = sys.maxsize
    task_to_remove = None
    for task in potential_to_be_removed:
        task_occ = task_resource_occurences[task]
        # 3. If resource is not the only one performing that task, try remove task where resource influences the least.
        if len(task_occ) > 1:
            if task_occ[resource['id']] < lowest_number:
                lowest_number = task_occ[resource['id']]
                task_to_remove = task
    if task_to_remove is not None:

        resource['assigned_tasks'].remove(task_to_remove)

        resource_id = resource['id']
        with open(roster_manager.time_table, 'r') as t_read:
            ttb = json.load(t_read)
        resource_profiles = ttb['resource_profiles']
        task_resource_distribution = ttb['task_resource_distribution']
        resource_calendars = ttb['resource_calendars']

        # A. Enumerate resource_profiles and replace each occurrence with updated resource_profile
        for profile in resource_profiles:
            # If task_id == task that got removed from resource -> Remove resource from resource_list
            if profile['id'] == task_to_remove:
                for r_in_list in profile['resource_list']:
                    if r_in_list['id'] == resource_id:
                        profile['resource_list'].remove(r_in_list)
                        to_copy = copy.deepcopy(profile)
                        resource_profiles.remove(profile)
                        resource_profiles.append(to_copy)

            # For each task where resource also performs, update that resource_list entry with updated resource_profile
            for task_id in resource['assigned_tasks']:
                if profile['id'] == task_id:
                    for r_in_list in profile['resource_list']:
                        if r_in_list['id'] == resource_id:
                            profile['resource_list'].remove(r_in_list)
                            profile['resource_list'].append(resource)
                            to_copy = copy.deepcopy(profile)
                            resource_profiles.remove(profile)
                            resource_profiles.append(to_copy)

        # B. Enumerate task_resource_distributions and remove distro from task_to_remove
        for t_r_dis in task_resource_distribution:
            if t_r_dis['task_id'] == task_to_remove:
                for res in t_r_dis['resources']:
                    if res['resource_id'] == resource['id']:
                        t_r_dis['resources'].remove(res)
                        to_copy = copy.deepcopy(t_r_dis)
                        task_resource_distribution.remove(t_r_dis)
                        task_resource_distribution.append(to_copy)

        # C. Write updated information to JSON.

        rest_of_info = {'resource_profiles': resource_profiles,
                        'arrival_time_distribution': ttb['arrival_time_distribution'],
                        'arrival_time_calendar': ttb['arrival_time_calendar'],
                        'gateway_branching_probabilities': ttb['gateway_branching_probabilities'],
                        'task_resource_distribution': task_resource_distribution,
                        'event_distribution': ttb['event_distribution'],
                        'resource_calendars': resource_calendars}

        with open(roster_manager.time_table, 'w') as out:
            out.write(json.dumps(rest_of_info, indent=4))
        return True, RosterManager(roster_manager.roster.roster_name, roster_manager.time_table,
                                   roster_manager.constraints_json)
    return False, None


# 0. Find first occurrence of resource and rewrite assigned_tasks
# resource_task_profile = next((x for x in resource_profiles if x['id'] == task_to_remove), None)
# resource_profiles_list = resource_task_profile['resource_list']
# resource_to_be_copied = next((y for y in resource_profiles_list if y['id'] == resource_id), None)
# index = next((i for i, item in enumerate(resource_profiles_list) if item['id'] == resource_id), -1)

# new_profile = copy.deepcopy(resource_to_be_copied)
# new_profile['assigned_tasks'] = resource['assigned_tasks']

# 1. Remove task from resource profile
# del resource_task_profile['resource_list'][index]
# for index, item in enumerate(resource_profiles):
#     if item['id'] == task_to_remove:
#         resource_profiles[index] = resource_task_profile

# 2. For each task where resource performs, replace with new profile
# for profile in resource_profiles:
#     for res in profile['resource_list']:
#         if res['id'] == resource['id']:
#             profile['resource_list'].remove(res)
#             profile['resource_list'].append(new_profile)

# 3. For each task where resource no longer performs, remove task_resource_distribution


def resolve_remove_resource_json_information(resource, roster_manager):
    # 1 !!! MAKE BACKUP OF CONSTRAINTS AND TIMETABLE
    shutil.copyfile(roster_manager.time_table, roster_manager.temp_timetable)
    shutil.copyfile(roster_manager.constraints_json, roster_manager.temp_constraints)

    try:
        resource_id = resource['id']
        print("Try to remove " + resource_id)
        with open(roster_manager.time_table, 'r') as t_read:
            ttb = json.load(t_read)
        resource_profiles = ttb['resource_profiles']
        task_resource_distribution = ttb['task_resource_distribution']
        resource_calendars = ttb['resource_calendars']

        # A.
        for task_id in resource['assigned_tasks']:
            for profile in resource_profiles:
                if profile['id'] == task_id:
                    for r_in_list in profile['resource_list']:
                        if r_in_list['id'] == resource_id:
                            profile['resource_list'].remove(r_in_list)
                            to_copy = copy.deepcopy(profile)
                            resource_profiles.remove(profile)
                            resource_profiles.append(to_copy)

        # for profile in resource_profiles:
        #     # For each task where resource also performs, update that resource_list entry
        #     for task_id in resource['assigned_tasks']:
        #         if profile['id'] == task_id:
        #             for r_in_list in profile['resource_list']:
        #                 if r_in_list['id'] == resource_id:
        #                     profile['resource_list'].remove(r_in_list)
        #                     to_copy = copy.deepcopy(profile)
        #                     resource_profiles.remove(profile)
        #                     resource_profiles.append(to_copy)
        # B. Enumerate task_resource_distributions and remove distro from task_to_remove
        for task_id in resource['assigned_tasks']:
            for t_r_dis in task_resource_distribution:
                if t_r_dis['task_id'] == task_id:
                    for res in t_r_dis['resources']:
                        if res['resource_id'] == resource_id:
                            t_r_dis['resources'].remove(res)
                            to_copy = copy.deepcopy(t_r_dis)
                            task_resource_distribution.remove(t_r_dis)
                            task_resource_distribution.append(to_copy)

        resource_to_be_removed = next((x for x in resource_calendars if x['id'] == resource_id + "timetable"), None)
        resource_calendars.remove(resource_to_be_removed)

        # 5.2 After all changes have been made, overwrite JSON with timetable.
        rest_of_info = {'resource_profiles': resource_profiles,
                        'arrival_time_distribution': ttb['arrival_time_distribution'],
                        'arrival_time_calendar': ttb['arrival_time_calendar'],
                        'gateway_branching_probabilities': ttb['gateway_branching_probabilities'],
                        'task_resource_distribution': task_resource_distribution,
                        'event_distribution': ttb['event_distribution'],
                        'resource_calendars': resource_calendars}

        with open(roster_manager.time_table, 'w') as out:
            out.write(json.dumps(rest_of_info, indent=4))


        # 1. make changes to resource_profiles
        # resource_task_profile = next((x for x in resource_profiles if x['id'] == task_to_improve), None)
        # resource_profiles_list = resource_task_profile['resource_list']
        # resource_to_be_removed = next((y for y in resource_profiles_list if y['id'] == resource_id), None)

        # resource_profiles_list.remove(resource_to_be_removed)
        # resource_task_profile['resource_list'] = resource_profiles_list
        # 1.2 Replace entire resource_profile with new profile
        # for index, item in enumerate(resource_profiles):
        #     for item_resource in item['resource_list']:
        #         if item_resource['id'] == resource_id:
        #             item['resource_list'].remove(item_resource)

        # 2. make changes to task_resource_distributions
        # task_resource_distro = next((x for x in task_resource_distribution if x['task_id'] == task_to_improve), None)
        # task_profile_resource_list = task_resource_distro['resources']
        # resource_to_be_removed = next((y for y in task_profile_resource_list if y['resource_id'] == resource_id), None)
        #
        # task_profile_resource_list.remove(resource_to_be_removed)
        #
        # task_resource_distro['resources'] = task_profile_resource_list
        #
        # for index, item in enumerate(task_resource_distribution):
        #     for item_resource in item['resources']:
        #         if item_resource['resource_id'] == resource_id:
        #             item['resources'].remove(item_resource)
            # if item['task_id'] == task_to_improve:
            #     del task_resource_distribution[index]

        # 3. Make changes to resource calendar
        # resource_to_be_removed = next((x for x in resource_calendars if x['id'] == resource_id + "timetable"), None)
        # resource_calendars.remove(resource_to_be_removed)

        # 4. Make changes to constraints json
        with open(roster_manager.constraints_json, 'r') as c_read:
            cons = json.load(c_read)

        constraint_profiles = cons['resources']
        constraints_to_be_removed = next((x for x in constraint_profiles if x['id'] == resource_id + "timetable"), None)
        constraint_profiles.remove(constraints_to_be_removed)

        # 5.1 After all changes have been made, overwrite JSON with constraints.
        constraints_info = {'time_var': cons['time_var'],
                            'max_cap': cons['max_cap'],
                            'max_shift_size': cons['max_shift_size'],
                            'max_shift_blocks': cons['max_shift_blocks'],
                            'hours_in_day': cons['hours_in_day'],
                            'resources': constraint_profiles}

        with open(roster_manager.constraints_json, 'w') as c_write:
            c_write.write(json.dumps(constraints_info, indent=4))

        print("JUST BEFORE RETURN TRUE")
        return True, RosterManager(roster_manager.roster.roster_name, roster_manager.time_table,
                                   roster_manager.constraints_json)
    except Exception as n:
        raise Exception(n)
        return False, None


def resolve_add_resource_json_information(resource, roster_manager, task_to_improve):
    shutil.copyfile(roster_manager.time_table, roster_manager.temp_timetable)
    shutil.copyfile(roster_manager.constraints_json, roster_manager.temp_constraints)
    # Step 1: Create copy of current timetable.json and constraints.json
    try:
        # Collect timetable information that will be modified
        resource_id = resource['id']
        with open(roster_manager.time_table, 'r') as t_read:
            ttb = json.load(t_read)
        resource_profiles = ttb['resource_profiles']
        task_resource_distribution = ttb['task_resource_distribution']
        resource_calendars = ttb['resource_calendars']

        to_be_added = copy.deepcopy(resource)
        k = str(time.time()).encode('utf-8')
        h = hashlib.blake2b(key=k, digest_size=16)

        # Add hex digests to create unique id's for new copies
        # Add only task_to_improve as assigned_tasks
        # 1.1 Make changes to new_profile
        to_be_added['id'] += "_COPY" + h.hexdigest()[:10]
        to_be_added['name'] += "_COPY" + h.hexdigest()[:10]
        to_be_added['calendar'] = resource_id + "_COPY" + h.hexdigest()[:10] + "timetable"
        to_be_added['assigned_tasks'] = [task_to_improve]

        for profile in resource_profiles:
            if profile['id'] == task_to_improve:
                profile['resource_list'].append(to_be_added)
                profile_copy = copy.deepcopy(profile)
                resource_profiles.remove(profile)
                resource_profiles.append(profile_copy)


        for task_distr in task_resource_distribution:
            if task_distr['task_id'] == task_to_improve:
                for t_d_r in task_distr['resources']:
                    if t_d_r['resource_id'] == resource_id:
                        t_d_r_to_add = copy.deepcopy(t_d_r)
                        t_d_r_to_add['resource_id'] += "_COPY" + h.hexdigest()[:10]
                        task_distr['resources'].append(t_d_r_to_add)

                        task_distr_copy = copy.deepcopy(task_distr)
                        task_resource_distribution.remove(task_distr)
                        task_resource_distribution.append(task_distr_copy)

        for r_calendar in resource_calendars:
            if r_calendar['id'] == resource_id+"timetable":
                calendar_to_be_added = copy.deepcopy(r_calendar)
                calendar_to_be_added['id'] = resource_id + "_COPY" + h.hexdigest()[:10] + "timetable"
                calendar_to_be_added['name'] = resource_id + "_COPY" + h.hexdigest()[:10] + "timetable"
                resource_calendars.append(calendar_to_be_added)

        rest_of_info = {'resource_profiles': resource_profiles,
                        'arrival_time_distribution': ttb['arrival_time_distribution'],
                        'arrival_time_calendar': ttb['arrival_time_calendar'],
                        'gateway_branching_probabilities': ttb['gateway_branching_probabilities'],
                        'task_resource_distribution': task_resource_distribution,
                        'event_distribution': ttb['event_distribution'],
                        'resource_calendars': resource_calendars}

        with open(roster_manager.time_table, 'w') as out:
            out.write(json.dumps(rest_of_info, indent=4))


        with open(roster_manager.constraints_json, 'r') as c_read:
            cons = json.load(c_read)
        constraint_profiles = cons['resources']

        for c_profile in constraint_profiles:
            if c_profile['id'] == resource_id+"timetable":
                cons_to_be_added = copy.deepcopy(c_profile)
                cons_to_be_added['id'] = resource_id + "_COPY" + h.hexdigest()[:10] + "timetable"
                constraint_profiles.append(cons_to_be_added)

        constraints_info = {'time_var': cons['time_var'],
                            'max_cap': cons['max_cap'],
                            'max_shift_size': cons['max_shift_size'],
                            'max_shift_blocks': cons['max_shift_blocks'],
                            'hours_in_day': cons['hours_in_day'],
                            'resources': constraint_profiles}

        with open(roster_manager.constraints_json, 'w') as t_write:
            t_write.write(json.dumps(constraints_info, indent=4))

        return True, RosterManager(roster_manager.roster.roster_name, roster_manager.time_table,
                                   roster_manager.constraints_json)

        # 1. Get resource_profile to copy
        # resource_task_profile = next((x for x in resource_profiles if x['id'] == task_to_improve), None)
        # resource_profiles_list = resource_task_profile['resource_list']
        # resource_to_be_copied = next((y for y in resource_profiles_list if y['id'] == resource_id), None)
        # new_profile = copy.deepcopy(resource_to_be_copied)



        # Add new profile to resource_profiles_list
        # resource_profiles_list.append(new_profile)
        # resource_task_profile['resource_list'] = resource_profiles_list

        # 1.2 Replace entire resource_profile with new profile
        # for index, item in enumerate(resource_profiles):
        #     if item['id'] == task_to_improve:
        #         resource_profiles[index] = resource_task_profile

        # 2. make changes to task_resource_distributions
        # task_resource_distro = next((x for x in task_resource_distribution if x['task_id'] == task_to_improve), None)
        # task_profile_resource_list = task_resource_distro['resources']
        # resource_to_be_copied = next((y for y in task_profile_resource_list if y['resource_id'] == resource_id), None)
        # new_distribution = copy.deepcopy(resource_to_be_copied)
        # new_distribution['resource_id'] += "_COPY" + h.hexdigest()[:10]
        # task_profile_resource_list.append(new_distribution)
        #
        # task_resource_distro['resources'] = task_profile_resource_list
        #
        # for index, item in enumerate(task_resource_distribution):
        #     if item['task_id'] == task_to_improve:
        #         task_resource_distribution[index] = task_resource_distro
        #
        # # 3. Make changes to resource calendar
        # resource_to_be_copied = next((x for x in resource_calendars if x['id'] == resource_id + "timetable"), None)
        # new_resource = copy.deepcopy(resource_to_be_copied)
        # new_resource['id'] = resource_id + "_COPY" + h.hexdigest()[:10] + "timetable"
        # new_resource['name'] = new_resource['id']

        # resource_calendars.append(new_resource)

        # 4. Make changes to constraints json
        # with open(roster_manager.constraints_json, 'r') as c_read:
        #     cons = json.load(c_read)
        # constraint_profiles = cons['resources']
        # constraints_to_be_copied = next((x for x in constraint_profiles if x['id'] == resource_id + "timetable"), None)
        # new_constraints = copy.deepcopy(constraints_to_be_copied)
        # new_constraints['id'] = resource_id + "_COPY" + h.hexdigest()[:10] + "timetable"
        #
        # constraint_profiles.append(new_constraints)
        # 5.1 After all changes have been made, overwrite JSON with constraints.

        # 5.2 After all changes have been made, overwrite JSON with timetable.

    except Exception as n:
        raise Exception(n)
        return False, None


def resolve_add_resources_in_process(iteration_info, iterations_handler, iterations_count, roster_manager):
    pools_info, simulation_info, distance = iteration_info[0], iteration_info[1], iteration_info[2]
    if pools_info is None:
        return None
    iterations_count[0] += 1
    # Collection of information for function
    events = {}
    task_resource_occurrences = {}
    if len(iterations_handler.traces) > 0:
        for trace_list in iterations_handler.traces:
            for trace in trace_list.trace_list:
                for event in trace.event_list:
                    if event.task_id in task_resource_occurrences.keys():
                        if event.resource_id in task_resource_occurrences[event.task_id].keys():
                            task_resource_occurrences[event.task_id][event.resource_id] += 1
                        else:
                            task_resource_occurrences[event.task_id][event.resource_id] = 1
                    else:
                        task_resource_occurrences[event.task_id] = {}

                    if event.waiting_time > 0.0:
                        if event.task_id in events.keys():
                            events[event.task_id] += 1
                        else:
                            events[event.task_id] = 1
                    if event.idle_time > 0.0:
                        if event.task_id in events.keys():
                            events[event.task_id] += 1
                        else:
                            events[event.task_id] = 1
    tasks_to_improve = sort_tasks_by_most_occurrences(events)

    # For each task, sorted by most impactful.
    for task in tasks_to_improve:
        task_info = pools_info.task_pools[task]
        # Only 1 resource is assigned to this task
        if len(task_info) == 1:
            resource = task_info[0]
            print("WT - ADD " + resource['id'])
            # Resource has only this task assigned.
            if len(resource['assigned_tasks']) == 1:
                # Only solution here is to make a copy and add
                ready_to_sim = resolve_add_resource_json_information(resource, roster_manager, task)
                if ready_to_sim[0]:
                    new_res_manager = ready_to_sim[1]
                    iterations_handler.resource_manager = new_res_manager
                    iterations_handler.time_table_path = new_res_manager.time_table
                    new_pools_info = PoolInfo(new_res_manager.get_all_resources_in_dict(),
                                              new_res_manager.get_task_pools())

                    if _try_solution_new_resource(new_pools_info, iterations_handler, distance):
                        return True
                    else:
                        print("sim w/ removed resource discarded - resetting timetables")
                        shutil.copyfile(roster_manager.temp_timetable, roster_manager.time_table)
                        shutil.copyfile(roster_manager.temp_constraints, roster_manager.constraints_json)

                        new_res_manager = RosterManager(roster_manager.roster.roster_name, roster_manager.time_table,
                                                        roster_manager.constraints_json)
                        iterations_handler.resource_manager = new_res_manager
                        iterations_handler.time_table_path = new_res_manager.time_table
                else:
                    # Replace timetable and constraints with updated jsons.
                    print("Ready sim failed - resetting timetables")
                    shutil.copyfile(roster_manager.temp_timetable, roster_manager.time_table)
                    shutil.copyfile(roster_manager.temp_constraints, roster_manager.constraints_json)

            else:
                # Try to remove other task(s) from resource
                ready_to_sim = resolve_reschedule_resource_json_information(resource, roster_manager,
                                                                            task,
                                                                            task_resource_occurrences)
                if ready_to_sim[0]:
                    new_res_manager = ready_to_sim[1]
                    iterations_handler.resource_manager = new_res_manager
                    iterations_handler.time_table_path = new_res_manager.time_table
                    new_pools_info = PoolInfo(new_res_manager.get_all_resources_in_dict(),
                                              new_res_manager.get_task_pools())

                    if _try_solution_new_resource(new_pools_info, iterations_handler, distance):
                        return True
                    else:
                        shutil.copyfile(roster_manager.temp_timetable, roster_manager.time_table)
                        shutil.copyfile(roster_manager.temp_constraints, roster_manager.constraints_json)

                        new_res_manager = RosterManager(roster_manager.roster.roster_name, roster_manager.time_table,
                                                        roster_manager.constraints_json)
                        iterations_handler.resource_manager = new_res_manager
                        iterations_handler.time_table_path = new_res_manager.time_table

                        # Don't return false, try to add new resource.
                        # ready_to_sim = resolve_add_resource_json_information(resource, roster_manager,
                        #                                                      task)

                        # if ready_to_sim[0]:
                        #     # TODO SIM
                        #     new_res_manager = ready_to_sim[1]
                        #     iterations_handler.resource_manager = new_res_manager
                        #     iterations_handler.time_table_path = new_res_manager.time_table
                        #     new_pools_info = PoolInfo(new_res_manager.get_all_resources_in_dict(),
                        #                               new_res_manager.get_task_pools())
                        #
                        #     if _try_solution_new_resource(new_pools_info, iterations_handler, distance):
                        #         return True
                        #     else:
                        #         shutil.copyfile(roster_manager.temp_timetable, roster_manager.time_table)
                        #         shutil.copyfile(roster_manager.temp_constraints, roster_manager.constraints_json)
                        #         new_res_manager = RosterManager(roster_manager.roster.roster_name,
                        #                                         roster_manager.time_table,
                        #                                         roster_manager.constraints_json)
                        #         iterations_handler.resource_manager = new_res_manager
                        #         iterations_handler.time_table_path = new_res_manager.time_table
                else:
                    # Replace timetable and constraints with updated jsons.
                    print("sim w/ removed resource discarded - resetting timetables")
                    shutil.copyfile(roster_manager.temp_timetable, roster_manager.time_table)
                    shutil.copyfile(roster_manager.temp_constraints, roster_manager.constraints_json)

        elif len(task_info) > 1:
            # count the occurences of which a resource performed said task
            # Take the one with the lowest # and check its tasks, try remove one of its tasks from the list
            resources_and_occurences = {}
            for trace_list in iterations_handler.traces:
                for trace in trace_list.trace_list:
                    for event in trace.event_list:
                        if event.task_id == task:
                            if event.waiting_time > 0.0 or event.idle_time > 0.0:
                                if event.resource_id in resources_and_occurences.keys():
                                    resources_and_occurences[event.resource_id] += 1
                                else:
                                    resources_and_occurences[event.resource_id] = 1
            # Sort by resource with highest impact on WT/IT
            sorted_resources = sort_tasks_by_most_occurrences(resources_and_occurences)
            task_info_sorted_by_occurences = []
            for resource in sorted_resources:
                for tir in task_info:
                    if tir['id'] == resource:
                        task_info_sorted_by_occurences.append(tir)

            for resource in task_info_sorted_by_occurences:
                if len(resource['assigned_tasks']) > 1:
                    # Only try reschedule on resources with more than 1 task -> IF THIS DOES NOT IMPROVE THEN WE NEED TO RESET.
                    ready_to_sim = resolve_reschedule_resource_json_information(resource, roster_manager,
                                                                                task,
                                                                                task_resource_occurrences)
                    if ready_to_sim[0]:
                        new_res_manager = ready_to_sim[1]
                        iterations_handler.resource_manager = new_res_manager
                        iterations_handler.time_table_path = new_res_manager.time_table
                        new_pools_info = PoolInfo(new_res_manager.get_all_resources_in_dict(),
                                                  new_res_manager.get_task_pools())

                        if _try_solution_new_resource(new_pools_info, iterations_handler, distance):
                            return True
                        else:
                            shutil.copyfile(roster_manager.temp_timetable, roster_manager.time_table)
                            shutil.copyfile(roster_manager.temp_constraints, roster_manager.constraints_json)
                            new_res_manager = RosterManager(roster_manager.roster.roster_name,
                                                            roster_manager.time_table,
                                                            roster_manager.constraints_json)
                            iterations_handler.resource_manager = new_res_manager
                            iterations_handler.time_table_path = new_res_manager.time_table


                            # Dont return false, try to add new resource.
                            # ready_to_sim = resolve_add_resource_json_information(resource, roster_manager,
                            #                                                      task)

                            # if ready_to_sim[0]:
                            #     # TODO SIM
                            #     new_res_manager = ready_to_sim[1]
                            #     iterations_handler.resource_manager = new_res_manager
                            #     iterations_handler.time_table_path = new_res_manager.time_table
                            #     new_pools_info = PoolInfo(new_res_manager.get_all_resources_in_dict(),
                            #                               new_res_manager.get_task_pools())
                            #
                            #     if _try_solution_new_resource(new_pools_info, iterations_handler, distance):
                            #         return True
                            #     else:
                            #         shutil.copyfile(roster_manager.temp_timetable, roster_manager.time_table)
                            #         shutil.copyfile(roster_manager.temp_constraints, roster_manager.constraints_json)
                            #         new_res_manager = RosterManager(roster_manager.roster.roster_name,
                            #                                         roster_manager.time_table,
                            #                                         roster_manager.constraints_json)
                            #         iterations_handler.resource_manager = new_res_manager
                            #         iterations_handler.time_table_path = new_res_manager.time_table
                    else:
                        # Replace timetable and constraints with updated jsons.
                        shutil.copyfile(roster_manager.temp_timetable, roster_manager.time_table)
                        shutil.copyfile(roster_manager.temp_constraints, roster_manager.constraints_json)
            # Only get here when no improvements are found
            # Find resource with the smallest schedule in task, use as copy
            print("*"*10)
            print("A and B step offered no result added to pareto, try last options before moving on.")
            resources_just_occurrences = {}
            for trace_list in iterations_handler.traces:
                for trace in trace_list.trace_list:
                    for event in trace.event_list:
                        if event.task_id == task:
                            if event.resource_id in resources_just_occurrences.keys():
                                resources_just_occurrences[event.resource_id] += 1
                            else:
                                resources_just_occurrences[event.resource_id] = 1
            sorted_resources = sort_tasks_by_most_occurrences(resources_just_occurrences)
            sorted_resources.reverse()

            for t in task_info:
                if t['id'] == sorted_resources[0]:
                    resource_to_resolve = t
            ready_to_sim = resolve_add_resource_json_information(resource_to_resolve, roster_manager,
                                                                 task)
            if ready_to_sim[0]:
                new_res_manager = ready_to_sim[1]
                iterations_handler.resource_manager = new_res_manager
                iterations_handler.time_table_path = new_res_manager.time_table
                new_pools_info = PoolInfo(new_res_manager.get_all_resources_in_dict(), new_res_manager.get_task_pools())

                if _try_solution_new_resource(new_pools_info, iterations_handler, distance):
                    return True
                else:
                    # Replace timetable and constraints with updated jsons.
                    shutil.copyfile(roster_manager.temp_timetable, roster_manager.time_table)
                    shutil.copyfile(roster_manager.temp_constraints, roster_manager.constraints_json)
                    new_res_manager = RosterManager(roster_manager.roster.roster_name, roster_manager.time_table,
                                                    roster_manager.constraints_json)
                    iterations_handler.resource_manager = new_res_manager
                    iterations_handler.time_table_path = new_res_manager.time_table
            else:
                # Replace timetable and constraints with updated jsons.
                shutil.copyfile(roster_manager.temp_timetable, roster_manager.time_table)
                shutil.copyfile(roster_manager.temp_constraints, roster_manager.constraints_json)

    return False


def sort_tasks_by_most_occurrences(dictionary):
    res = []
    for k, li in dictionary.items():
        r = [k, li]
        res.append(r)

    return [out[0] for out in sorted(res, key=lambda x: x[1], reverse=True)]


def sort_resources_by_utilization(dct):
    res = []
    for k, util in dct.items():
        r = [k, util]
        res.append(r)
    out_list = sorted(res, key=lambda x: x[1], reverse=True)
    out_list = [out[0] for out in out_list]
    return out_list


def solution_traces_add_new_shift(iteration_info, iterations_handler, iterations_count, accessible_bits,
                                  resource_masks):
    pools_info, simulation_info, distance = iteration_info[0], iteration_info[1], iteration_info[2]
    if pools_info is None:
        return None
    iterations_count[0] += 1

    resources = sort_resources_by_utilization(simulation_info.pool_utilization)

    actual_resource_info = []
    resource_works_when = {}
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    for pool in resources:
        if len(iterations_handler.traces) > 0:
            for trace_list in iterations_handler.traces:
                for trace in trace_list.trace_list:
                    for event in trace.event_list:
                        if event.resource_id == pool:
                            if event.started_datetime.weekday() in resource_works_when.keys():
                                r = resource_works_when[event.started_datetime.weekday()]
                                r += 1
                            else:
                                resource_works_when[event.started_datetime.weekday()] = 1

        actual_resource_info.append(pools_info.pools[pool])
        resource_copy = copy.deepcopy(actual_resource_info)
        most_occurring_day = sort_by_most_occuring_day(resource_works_when)

        for resource in resource_copy:
            if not resource.is_human:
                continue
            day = days[most_occurring_day[0]]
            shift_arr = _bitmap_to_valid_structure(resource.shifts[day][0], 1)
            indexes = []
            i_idx = 0
            for idx in range(len(shift_arr)):
                # Collect all shift blocks outer indexes
                if shift_arr[idx] == 1 and shift_arr[idx - 1] == 0:
                    indexes.append([0, 0])
                    indexes[i_idx][0] = idx
                if shift_arr[idx] == 1 and shift_arr[idx + 1] == 0:
                    indexes[i_idx][1] = idx
                    i_idx += 1

            for block in range(len(indexes)):
                l_idx = indexes[block][0]
                r_idx = indexes[block][1]

                shift_arr[r_idx + 2] = 1
                resource.set_shifts(_list_to_binary(shift_arr), day)
                if resource.verify_timetable(day):
                    break

                # No valid move, reset and go next
                shift_arr[r_idx + 2] = 0
                resource.set_shifts(_list_to_binary(shift_arr), day)

            # Options have been tested, try simulate
            if _try_solution(resource_copy, pools_info, iterations_handler, distance):
                return True

    return True


def solution_sorting_by_pool_outturn(iteration_info, iterations_handler, iterations_count, accessible_bits,
                                     resource_masks):
    pools_info, simulation_info, distance = iteration_info[0], iteration_info[1], iteration_info[2]
    if pools_info is None:
        return
    iterations_count[0] += 1
    # sorting pools by quality

    sorted_pools = [
        sorted(pools_info.pools.items(), key=lambda x: simulation_info.pool_cost_outturn(x[1].resource_name),
               reverse=True),
        sorted(pools_info.pools.items(), key=lambda x: simulation_info.pool_time_outturn(x[1].resource_name),
               reverse=True)]

    mean_outturn = [0, 0]
    for pool in sorted_pools[0]:
        mean_outturn[0] += simulation_info.pool_cost_outturn(pool[0])
        mean_outturn[1] += simulation_info.pool_time_outturn(pool[0])
    mean_outturn[0] /= len(sorted_pools[0])
    mean_outturn[1] /= len(sorted_pools[1])
    for i in range(0, 2):
        by_time = False if i == 0 else True
        for pool in sorted_pools[i]:
            r_name = pool[0]
            outturn = simulation_info.pool_cost_outturn(r_name) if i == 0 else simulation_info.pool_time_outturn(
                r_name)
            if outturn > mean_outturn[i]:
                fix_pool_outturn(r_name, pools_info, iterations_handler, accessible_bits, distance, by_time,
                                 accessible_bits)
            else:
                break
    return


def fix_pool_outturn(pool_name, pools_info, iterations_handler, accessible_bits, distance, by_time, resource_masks):
    amounts = []
    if by_time:
        amounts = [1]
    else:
        if pools_info.pools[pool_name].total_amount > 1:
            amounts = [-1]
    # TODO How to process this?
    # return False if len(amounts) == 0 else \
    #     _generate_solutions(iterations_handler, accessible_bits, pools_info, pool_name, distance, accessible_bits)


def solution_traces_sorting_by_idle_times(iteration_info, iterations_handler, iterations_count, resource_manager):
    # # Retrieving info of solution closer to the optimal which has not been processed yet
    pools_info, simulation_info, distance = iteration_info[0], iteration_info[1], iteration_info[2]
    if pools_info is None:
        return None
    iterations_count[0] += 1

    # Collect for each trace, the information of which task was executed on which day
    tasks_with_idle_occurrences = {}
    tasks_with_idle = {}
    resources_and_occurrences = {}
    if len(iterations_handler.traces) > 0:
        for trace_list in iterations_handler.traces:
            for trace in trace_list.trace_list:
                for event in trace.event_list:
                    if event.idle_time > 0.0:
                        if event.task_id in tasks_with_idle_occurrences.keys():
                            if event.started_datetime.weekday() in tasks_with_idle_occurrences[event.task_id].keys():
                                r = tasks_with_idle_occurrences[event.task_id]
                                r[event.started_datetime.weekday()] += 1
                            else:
                                r = tasks_with_idle_occurrences[event.task_id]
                                r[event.started_datetime.weekday()] = 1

                            r = tasks_with_idle[event.task_id]
                            tasks_with_idle[event.task_id] = [r[0] + event.idle_time, r[1] + 1]

                            if event.resource_id in resources_and_occurrences[event.task_id].keys():
                                resources_and_occurrences[event.task_id][event.resource_id] += 1
                            else:
                                resources_and_occurrences[event.task_id][event.resource_id] = 1
                        else:
                            tasks_with_idle_occurrences[event.task_id] = {}
                            tasks_with_idle[event.task_id] = [event.idle_time, 1]
                            resources_and_occurrences[event.task_id] = {}

    sorted_tasks_by_idle_time = sort_tasks_by_idle_time(tasks_with_idle)

    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    for task in sorted_tasks_by_idle_time:
        task_to_do = task
        day_to_optimize = sort_by_most_occuring_day(tasks_with_idle_occurrences[task_to_do])
        resource_to_optimize = sorted(resources_and_occurrences[task_to_do],
                                      key=resources_and_occurrences[task_to_do].get)
        resources_who_can_do_task = pools_info.task_pools[task_to_do]

        actual_resource_info = []
        for resource in resources_who_can_do_task:
            for res in resource_to_optimize:
                if resource['id'] == res:
                    actual_resource_info.append(pools_info.pools[resource['id']])

        resource_copy = actual_resource_info
        for resource in resource_copy:
            print("IT - Resource " + resource.id)

            for day_int in day_to_optimize:
                day = days[day_int]

                shift_arr = _bitmap_to_valid_structure(resource.shifts[day][0], 1)
                indexes = []
                i_idx = 0
                for idx in range(len(shift_arr)):
                    # Collect all shift blocks outer indexes
                    if shift_arr[idx] == 1 and shift_arr[idx - 1] == 0:
                        indexes.append([0, 0])
                        indexes[i_idx][0] = idx
                    if shift_arr[idx] == 1 and shift_arr[idx + 1] == 0:
                        indexes[i_idx][1] = idx
                        i_idx += 1
                # TODO after finishing loop, try adding left, else try moving whole shift left
                for block in range(len(indexes)):
                    l_idx = indexes[block][0]
                    r_idx = indexes[block][1]

                    shift_arr[r_idx + 1] = 1
                    shift_arr[l_idx] = 1
                    resource.set_shifts(_list_to_binary(shift_arr), day)
                    if resource.verify_timetable(day):
                        # Adding left is valid, run sim
                        if _try_solution(resource_copy, pools_info, iterations_handler, distance):
                            return True

                    shift_arr[r_idx + 1] = 1
                    shift_arr[l_idx] = 0
                    resource.set_shifts(_list_to_binary(shift_arr), day)
                    if resource.verify_timetable(day):
                        # Moving left is valid, run sim
                        if _try_solution(resource_copy, pools_info, iterations_handler, distance):
                            return True
                    # No valid move, reset and go next
                    shift_arr[r_idx + 1] = 0
                    shift_arr[l_idx] = 1
                    resource.set_shifts(_list_to_binary(shift_arr), day)
        # All moves and resources on this task have been tried, stop.
        return False
    return False


def solution_traces_optimize_cost(iteration_info, iterations_handler, iterations_count, resource_manager):
    pools_info, simulation_info, distance = iteration_info[0], iteration_info[1], iteration_info[2]
    if pools_info is None:
        return None
    iterations_count[0] += 1
    # Retrieving info of solution closer to the optimal which has not been processed yet
    # pools_info, simulation_info, distance = iteration_info[0], iteration_info[1], iteration_info[2]
    # if pools_info is None:
    #     return None
    # iterations_count[0] += 1

    resources_to_optimize = {}
    # the first resource in pool_cost is the most expensive, the resource must also be a HUMAN resource
    for pool in simulation_info.pools_info.pools:
        if simulation_info.pools_info.pools[pool].is_human:
            pool_cost = simulation_info.pools_info.pools[pool].cost_per_hour * simulation_info.available_time[pool]
            resources_to_optimize[pool] = pool_cost

    resource_to_optimize = sort_resource_by_cost(resources_to_optimize)
    resource_to_optimize = resource_to_optimize[0]
    # Collect for each trace, the information of which task was executed on which day
    tasks_of_resource = []
    for task in pools_info.task_pools:
        for resource in pools_info.task_pools[task]:
            if resource['id'] == resource_to_optimize:
                tasks_of_resource.append(task)

    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    for task in tasks_of_resource:
        # for res in resource_to_optimize:
        actual_resource_info = [pools_info.pools[resource_to_optimize]]
        resource_copy = copy.deepcopy(actual_resource_info)
        for resource in resource_copy:
            print("Cost - Resource " + resource.id)
            for day in days:
                shift_arr = _bitmap_to_valid_structure(resource.shifts[day][0], 1)
                indexes = []
                i_idx = 0
                for idx in range(len(shift_arr)):
                    # Collect all shift blocks outer indexes
                    if shift_arr[idx] == 1 and shift_arr[idx - 1] == 0:
                        indexes.append([0, 0])
                        indexes[i_idx][0] = idx
                    if shift_arr[idx] == 1 and shift_arr[idx + 1] == 0:
                        indexes[i_idx][1] = idx
                        i_idx += 1
                # Try reduce size both sides, try reduce left, try reduce right

                for block in range(len(indexes)):
                    l_idx = indexes[block][0]
                    r_idx = indexes[block][1]

                    shift_arr[r_idx] = 0
                    shift_arr[l_idx] = 0
                    resource.set_shifts(_list_to_binary(shift_arr), day)
                    if resource.verify_timetable(day):
                        # Adding left is valid, run sim
                        if _try_solution(resource_copy, pools_info, iterations_handler, distance):
                            return True
                    shift_arr[r_idx] = 1
                    shift_arr[l_idx] = 0
                    resource.set_shifts(_list_to_binary(shift_arr), day)
                    if resource.verify_timetable(day):
                        # Moving left is valid, run sim
                        if _try_solution(resource_copy, pools_info, iterations_handler, distance):
                            return True

                    shift_arr[r_idx] = 0
                    shift_arr[l_idx] = 1
                    resource.set_shifts(_list_to_binary(shift_arr), day)
                    if resource.verify_timetable(day):
                        # Adding left is valid, run sim
                        if _try_solution(resource_copy, pools_info, iterations_handler, distance):
                            return True

                    # No valid move, reset and go next
                    shift_arr[r_idx] = 1
                    shift_arr[l_idx] = 1
                    resource.set_shifts(_list_to_binary(shift_arr), day)
        # All moves and resources on this task have been tried, stop.
        return False
    return False


def solution_traces_sorting_by_waiting_times(iteration_info, iterations_handler, iterations_count, resource_manager):
    pools_info, simulation_info, distance = iteration_info[0], iteration_info[1], iteration_info[2]
    if pools_info is None:
        return None
    iterations_count[0] += 1
    # Retrieving info of solution closer to the optimal which has not been processed yet
    # pools_info, simulation_info, distance = iteration_info[0], iteration_info[1], iteration_info[2]
    # if pools_info is None:
    #     return None
    # iterations_count[0] += 1

    # Collect for each trace, the information of which task was executed on which day
    tasks_with_wt_occurrences = {}
    tasks_with_wt = {}
    resources_and_occurrences = {}
    if len(iterations_handler.traces) > 0:
        for trace_list in iterations_handler.traces:
            for trace in trace_list.trace_list:
                for event in trace.event_list:
                    if event.waiting_time > 0.0:
                        if event.task_id in tasks_with_wt_occurrences.keys():
                            if event.enabled_datetime.weekday() in tasks_with_wt_occurrences[event.task_id].keys():
                                r = tasks_with_wt_occurrences[event.task_id]
                                r[event.enabled_datetime.weekday()] += 1
                            else:
                                r = tasks_with_wt_occurrences[event.task_id]
                                r[event.enabled_datetime.weekday()] = 1

                            r = tasks_with_wt[event.task_id]
                            tasks_with_wt[event.task_id] = [r[0] + event.waiting_time, r[1] + 1]

                            if event.resource_id in resources_and_occurrences[event.task_id].keys():
                                resources_and_occurrences[event.task_id][event.resource_id] += 1
                            else:
                                resources_and_occurrences[event.task_id][event.resource_id] = 1
                        else:
                            tasks_with_wt_occurrences[event.task_id] = {}
                            tasks_with_wt[event.task_id] = [event.waiting_time, 1]
                            resources_and_occurrences[event.task_id] = {}

    sorted_tasks_by_waiting_time = sort_tasks_by_waiting_time(tasks_with_wt)

    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    for task in sorted_tasks_by_waiting_time:
        task_to_do = task
        day_to_optimize = sort_by_most_occuring_day(tasks_with_wt_occurrences[task_to_do])
        resource_to_optimize = sorted(resources_and_occurrences[task_to_do],
                                      key=resources_and_occurrences[task_to_do].get)
        resources_who_can_do_task = pools_info.task_pools[task_to_do]

        actual_resource_info = []
        for resource in resources_who_can_do_task:
            for res in resource_to_optimize:
                if resource['id'] == res:
                    actual_resource_info.append(pools_info.pools[resource['id']])

        # resource_copy = copy.deepcopy(actual_resource_info)
        resource_copy = actual_resource_info

        for resource in resource_copy:
            print("WT - Resource " + resource.id)
            for day_int in day_to_optimize:
                day = days[day_int]

                shift_arr = _bitmap_to_valid_structure(resource.shifts[day][0], 1)
                indexes = []
                i_idx = 0
                for idx in range(len(shift_arr)):
                    # Collect all shift blocks outer indexes
                    if shift_arr[idx] == 1 and shift_arr[idx - 1] == 0:
                        indexes.append([0, 0])
                        indexes[i_idx][0] = idx
                    if shift_arr[idx] == 1 and shift_arr[idx + 1] == 0:
                        indexes[i_idx][1] = idx
                        i_idx += 1
                for block in range(len(indexes)):
                    l_idx = indexes[block][0]
                    r_idx = indexes[block][1]

                    shift_arr[l_idx - 1] = 1
                    shift_arr[r_idx] = 1
                    resource.set_shifts(_list_to_binary(shift_arr), day)
                    if resource.verify_timetable(day):
                        # Adding left is valid, run sim
                        if _try_solution(resource_copy, pools_info, iterations_handler, distance):
                            return True

                    shift_arr[l_idx - 1] = 1
                    shift_arr[r_idx] = 0
                    resource.set_shifts(_list_to_binary(shift_arr), day)
                    if resource.verify_timetable(day):
                        # Moving left is valid, run sim
                        if _try_solution(resource_copy, pools_info, iterations_handler, distance):
                            return True

                    # No valid move, reset and go next
                    shift_arr[l_idx - 1] = 0
                    shift_arr[r_idx] = 1
                    resource.set_shifts(_list_to_binary(shift_arr), day)
        # All moves and resources on this task have been tried, stop.
        return False
    return False


def _try_solution(resource_copy, pools_info, iterations_handler, distance):
    solution_found = False
    new_pools = copy.deepcopy(pools_info.pools)
    for res in resource_copy:
        for pool in new_pools:
            if pool == res.id:
                new_pools[pool] = res
                new_pools[pool].set_custom_id()

    if iterations_handler.try_new_solution(PoolInfo(new_pools, pools_info.task_pools), distance):
        solution_found = True

    return solution_found


def _try_solution_new_resource(pools_info, iterations_handler, distance):
    solution_found = False
    new_pools = copy.deepcopy(pools_info.pools)

    if iterations_handler.try_new_solution(PoolInfo(new_pools, pools_info.task_pools), distance):
        solution_found = True

    return solution_found


def sort_by_most_occuring_day(dict):
    return sorted(dict, key=dict.get, reverse=True)


def sort_tasks_by_idle_time(dict):
    res = []
    for k, li in dict.items():
        avg = li[0] / li[1]
        r = [k, avg]
        res.append(r)
    out_list = sorted(res, key=lambda x: x[1], reverse=True)
    out_list = [out[0] for out in out_list]
    return out_list


def sort_resource_by_cost(dict):
    res = []
    for k, cost in dict.items():
        res.append([k, cost])
    out_list = sorted(res, key=lambda x: x[1], reverse=True)
    out_list = [out[0] for out in out_list]
    return out_list


def sort_tasks_by_waiting_time(dict):
    res = []
    for k, li in dict.items():
        avg = li[0] / li[1]
        r = [k, avg]
        res.append(r)
    out_list = sorted(res, key=lambda x: x[1], reverse=True)
    out_list = [out[0] for out in out_list]
    return out_list


def solution_sorting_by_resource_utilization(iteration_info, iterations_handler, iterations_count, accessible_bits,
                                             resource_masks):
    # Retrieving info of solution closer to the optimal which has not been processed yet
    pools_info, simulation_info, distance = iteration_info[0], iteration_info[1], iteration_info[2]
    if pools_info is None:
        return None
    iterations_count[0] += 1
    sorted_pools = simulation_info.sort_pool_by_utilization()

    pool_utilization = simulation_info.pool_utilization
    is_fixed = [
        fix_busiest_pool(sorted_pools, pool_utilization, accessible_bits, pools_info, iterations_handler, distance),
        fix_laziest_pool(sorted_pools, pool_utilization, pools_info, accessible_bits, iterations_handler, distance),
        exchange_between_busiest_laziest(sorted_pools, pool_utilization, pools_info, iterations_handler, distance)
    ]

    return is_fixed[0] or is_fixed[1] or is_fixed[2]


def fix_busiest_pool(sorted_pools, pool_utilization, accessible_bits, pools_info, iterations_handler, distance):
    # Adding a resource to pool with highest resource utilization
    busiest_pools = _find_busiest_pools(sorted_pools, pool_utilization)
    is_improved = False
    for pool_name in busiest_pools:
        accessible_bits_resource = accessible_bits[pool_name]
        if _generate_solutions(iterations_handler, accessible_bits_resource, pools_info, pool_name, distance,
                               15):
            is_improved = True
    return is_improved


def fix_laziest_pool(sorted_pools, pool_utilization, pools_info, accessible_bits, iterations_handler, distance):
    # Removing a resource to pool with lowest resource utilization
    laziest_pools = _find_laziest_pools(sorted_pools, pool_utilization, pools_info)
    is_improved = False

    for pool_name in laziest_pools:
        accessible_bits_resource = accessible_bits[pool_name]
        if _generate_solutions(iterations_handler, accessible_bits_resource, pools_info, pool_name, distance,
                               15):
            is_improved = True
    return is_improved


def exchange_between_busiest_laziest(sorted_pools, pool_utilization, pools_info, iterations_handler, distance):
    # Retrieving pools with lowest resource utilization (laziest pools)
    laziest_pools = _find_laziest_pools(sorted_pools, pool_utilization, pools_info)
    # Retrieving pools with greater resource utilization (busiest pools)
    busiest_pools = _find_busiest_pools(sorted_pools, pool_utilization)
    # Exchanging resources between busiest and lasiest pools
    is_improved = False
    # TODO May need to revisit this.
    # for busiest in busiest_pools:
    #     for laziest in laziest_pools:
    #         if busiest == laziest:
    #             continue
    #         new_pools = copy.deepcopy(pools_info.pools)
    #         amount = min(_amount(pool_utilization[busiest], pools_info.pools[busiest].remaining_shifts['total']),
    #                      _amount(pool_utilization[laziest], pools_info.pools[laziest].remaining_shifts['total']))
    #         new_pools[busiest].set_total_amount(amount)
    #         new_pools[laziest].set_total_amount(-1 * amount)
    #
    #         if iterations_handler.try_new_solution(PoolInfo(new_pools, pools_info.task_pools), distance):
    #             is_improved = True
    return is_improved


def _find_laziest_pools(sorted_pools, pool_utilization, pools_info, proximity_index=0.1, upper_bound=0.7):
    i = len(sorted_pools) - 1
    laziest_pools = []
    min_r_utilization = 0
    while i >= 0:
        if pools_info.pools[sorted_pools[i]].is_human:
            laziest_pools.append(sorted_pools[i])
            min_r_utilization = pool_utilization[sorted_pools[i]]
            break
        i -= 1
    if len(laziest_pools) == 0:
        return laziest_pools
    while i - 1 >= 0:
        i -= 1
        r_utilization = pool_utilization[sorted_pools[i]]
        if r_utilization <= upper_bound or r_utilization - min_r_utilization < proximity_index:
            if pools_info.pools[sorted_pools[i]].is_human:
                laziest_pools.append(sorted_pools[i])
        else:
            break
    return laziest_pools


def _find_busiest_pools(sorted_pools, pool_utilization, proximity_index=0.1, lower_bound=0.7):
    busiest_pools = [sorted_pools[0]]
    max_r_utilization = pool_utilization[sorted_pools[0]]
    for i in range(1, len(sorted_pools)):
        r_utilization = pool_utilization[sorted_pools[i]]
        if r_utilization > lower_bound or max_r_utilization - r_utilization < proximity_index:
            busiest_pools.append(sorted_pools[i])
            continue
        break
    return busiest_pools


def random_shift(shifts, allowed_indexes):
    if len(allowed_indexes) != 0:
        for idx in allowed_indexes:
            shifts[idx] = random.randint(0, 1)
    return shifts


def _generate_solutions(iterations_handler, accessible_bits, pools_info, pool_name, distance, max_iterations):
    pools = pools_info.pools
    solution_found = False
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
    chosen_day = random.choice(days)
    new_pools = copy.deepcopy(pools)
    _valid = False
    for i in range(max_iterations):
        while not _valid:
            new_shifts = [0] * 24 * 1
            new_shifts = random_shift(new_shifts, accessible_bits[chosen_day])
            new_shifts = _list_to_binary(new_shifts) | new_pools[pool_name].shifts[chosen_day][0]
            new_pools[pool_name].set_shifts(new_shifts, chosen_day)
            new_pools[pool_name].set_custom_id()
            _valid = new_pools[pool_name].verify_timetable(chosen_day)
            if not _valid:
                # RESET if failed
                new_pools = copy.deepcopy(pools)

        if iterations_handler.try_new_solution(PoolInfo(new_pools, pools_info.task_pools), distance):
            solution_found = True
    return solution_found


def _amount(resource_utilization, current_amount):
    if resource_utilization < 0.7:
        return abs(int(resource_utilization * current_amount / 0.7) + 1 - current_amount)
    elif resource_utilization > 0.8:
        return abs(int(resource_utilization * current_amount / 0.8) + 1 - current_amount)
    return 1


def _sort_pools_by_quality(simulation_info, pools_info):
    # simulation_info.calculate_pool_quality(pools_info.task_pools, pools_info.pools)
    return sorted(pools_info.pools.items(), key=lambda x: simulation_info.pool_quality(x[1].name), reverse=True)


def set_up_cost(rm):
    # for resource in rm.get_all_resources():

    return ""
    # initial_pools_info = parse_simulation_model(rm)
    # if cost_model == 1:
    #     resource_costs = dict()
    # elif cost_model == 2:
    #     resource_costs = xes_log_info.calculate_resource_utilization(initial_pools_info.task_pools)
    # else:
    #     resource_costs = xes_log_info.calculate_resource_utilization(initial_pools_info.task_pools, True)
    # update_resource_cost(resource_costs)
    # return parse_simulation_model(rm)
