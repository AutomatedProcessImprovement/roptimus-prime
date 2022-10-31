import copy
from shutil import copyfile
import time
import datetime
import random
from new_version.data_structures.pools_info import PoolInfo
from new_version.pareto_algorithms_and_metrics.pareto_metrics import AlgorithmResults
from new_version.support_modules.file_manager import save_stats_file, read_stats_file
from new_version.support_modules.helpers import _list_to_binary
from new_version.support_modules.log_parser import extract_data_from_xes_event_log
from new_version.pareto_algorithms_and_metrics.iterations_handler import IterationHandler
from new_version.data_structures.RosterManager import RosterManager

temp_bpmn_file = './test_assets/CopiedModel.bpmn'


def hill_climb(log_name, xes_path, bpmn_path, time_table, constraints, max_func_ev, non_opt_ratio, tot_simulations,
               is_tabu):
    cost_type = 1

    # SETUP
    copyfile(bpmn_path, temp_bpmn_file)
    rm = RosterManager("DEFAULT_ROSTER2", time_table, constraints)

    starting_time = time.time()
    algorithm_name = 'tabu_srch' if is_tabu else 'hill_clmb'

    initial_pools_info = PoolInfo(rm.get_all_resources_in_dict(), rm.get_task_pools())
    it_handler = IterationHandler(log_name, initial_pools_info, tot_simulations, is_tabu, False, rm)
    max_iterations_reached = True
    # max_resources = initial_pools_info.total_resoures

    iterations_count = [0]

    while it_handler.solutions_count() < max_func_ev:
        if it_handler.pareto_update_distance >= non_opt_ratio * max_func_ev or not it_handler.has_next():
            max_iterations_reached = False
            break
        iteration_info = it_handler.next()
        solution_sorting_by_resource_utilization(iteration_info, it_handler, iterations_count,
                                                 rm.get_all_res_accessible_bits(), rm.get_all_res_masks())
        solution_sorting_by_pool_outturn(iteration_info, it_handler, iterations_count, rm.get_all_res_accessible_bits(),
                                         rm.get_all_res_masks())

    save_stats_file(log_name,
                    algorithm_name + '_without_mad',
                    # TODO With MAD?
                    # algorithm_name + ('_with_mad' if with_mad else '_without_mad'),
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
    # pool_name = random.choice(busiest_pools)
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
    # pool_name = random.choice(laziest_pools)

    for pool_name in laziest_pools:
        accessible_bits_resource = accessible_bits[pool_name]
    # amounts = [-1 * _amount(pool_utilization[pool_name], pools_info.pools[pool_name].total_amount), -1]
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
