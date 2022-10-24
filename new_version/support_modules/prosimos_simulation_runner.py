import multiprocessing

from diff_res_bpsim import run_simulation

import datetime
import re
import time

from new_version.data_structures.simulation_info import SimulationInfo
from new_version.data_structures.solution_space import DeviationInfo
from new_version.support_modules.file_manager import load_simulation_result
from new_version.support_modules.file_manager import save_simulation_results
from new_version.support_modules.file_manager import temp_bpmn_file


def process_simulations(model_file_path, json_path, total_cases, pools_info):
    starting_time = time.time()

    # Perform simulation with Prosimos -> Returns [{...}, {...}, {...}, sim_start, sim_end]
    result = run_simulation(model_file_path, json_path, total_cases)

    simulation_info = SimulationInfo(pools_info)
    simulation_info.simulation_time = time.time() - starting_time
    simulation_start_end = extract_simulation_dates_from_simulation_log(result)
    simulation_info.update_simulation_period(simulation_start_end[0], simulation_start_end[1])


    for i in result[2].keys():
        simulation_info.update_resource_utilization(result[2][i].r_profile.resource_id, result[2][i].utilization)
    for i in result[1].keys():
        simulation_info.add_task_statistics(pools_info.task_pools, i, float(result[1][i].idle_time.avg),
                                            float(result[1][i].duration.avg),
                                            pools_info.pools[pools_info.task_pools[i]].get_total_cost())
    simulation_info.mean_process_cycle_time = float(result[0].cycle_time.avg)

    return simulation_info


def perform_simulations(pools_info,
                        log_name,
                        simulations_count,
                        solution_index,
                        json_path,
                        model_file_path=temp_bpmn_file,
                        stat_out_path="./output_files/bimp_temp_files/output.csv",
                        starting_at=None):
    print("Running Simulation for Solution # %d (ID: %s) ..." % (solution_index, pools_info.id))
    simulated_info = load_simulation_result(log_name, pools_info)
    parallel_start_time = time.time()
    if simulated_info is not None:
        return simulated_info

    # Multiprocessing used to reduce total processing time, dependent on # cores in system
    pool = multiprocessing.Pool(5)
    async_results = [pool.apply_async(process_simulations, (model_file_path, json_path, 1500, pools_info)) for i in
                     range(simulations_count)]
    simulation_results = [ar.get() for ar in async_results]

    return estimate_median_absolute_deviation(pools_info, log_name, simulation_results, parallel_start_time)


def estimate_median_absolute_deviation(pools_info, log_name, simulation_results, parallel_start_time):
    by_cycle_time = sorted(simulation_results, key=lambda x: x.mean_process_cycle_time)
    by_duration = sorted(simulation_results, key=lambda x: x.simulation_duration())
    total_parallel_time = time.time() - parallel_start_time

    cycle_t_med = by_cycle_time[int(len(by_cycle_time) / 2)]
    duration_med = by_duration[int(len(by_duration) / 2)]

    c_times = list()
    duration = list()
    total_time = 0
    for i in range(0, len(by_cycle_time)):
        total_time += by_cycle_time[i].simulation_time
        c_times.append(abs(cycle_t_med.mean_process_cycle_time - by_cycle_time[i].mean_process_cycle_time))
        duration.append(abs(duration_med.simulation_duration() - by_duration[i].simulation_duration()))

    c_times = sorted(c_times)
    duration = sorted(duration)

    simulation_info = by_cycle_time[int(len(by_cycle_time) / 2)]
    simulation_info.deviation_info = DeviationInfo(c_times[int(len(c_times) / 2)], duration[int(len(duration) / 2)])

    print("Simulation Full Time:    %s" % str(datetime.timedelta(seconds=total_time)))
    print("Simulation Average Time: %s" % str(datetime.timedelta(seconds=(total_time / 15))))
    print("Simulation Parallel Time: %s" % str(datetime.timedelta(seconds=total_parallel_time)))
    save_simulation_results(log_name, pools_info, simulation_results, simulation_info)

    return simulation_info


def extract_simulation_dates_from_simulation_log(result):
    simulation_start_date = result[3]
    simulation_end_date = result[4]

    return [simulation_start_date, simulation_end_date]


def parse_date(date_str):
    return datetime.datetime.strptime(
        re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', date_str).group(), '%Y-%m-%d %H:%M:%S')
