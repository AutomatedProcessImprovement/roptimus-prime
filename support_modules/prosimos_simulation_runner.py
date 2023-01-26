from ext_tools.Prosimos.diff_res_bpsim import run_simulation
import datetime
import re
import time

from data_structures.simulation_info import SimulationInfo
from data_structures.solution_space import DeviationInfo
from support_modules.file_manager import save_simulation_results
from support_modules.file_manager import temp_bpmn_file
from ext_tools.Prosimos.bpdfr_simulation_engine.simulation_properties_parser import parse_json_sim_parameters


def process_simulations(model_file_path, json_path, total_cases, pools_info):
    starting_time = time.time()

    # Perform simulation with Prosimos -> Returns [{...}, {...}, {...}, sim_start, sim_end]
    (result, traces) = run_simulation(model_file_path, json_path, total_cases, starting_at="2023-01-01T00:00:00.000000+00:00") # ,

    _, cal_map, _, _, _, _ = parse_json_sim_parameters(json_path)

    simulation_info = SimulationInfo(pools_info)
    simulation_info.simulation_time = time.time() - starting_time
    simulation_start_end = extract_simulation_dates_from_simulation_log(result)
    simulation_info.update_simulation_period(simulation_start_end[0], simulation_start_end[1])

    for pool in pools_info.pools:
        if pool in result[2].keys():
            simulation_info.update_resource_utilization(result[2][pool].r_profile.resource_id, result[2][pool].utilization)
            simulation_info.update_resource_available_time(result[2][pool].r_profile.resource_id,
                                                           result[2][pool].available_time)
        else:
            simulation_info.update_resource_utilization(pool, 0)
            simulation_info.update_resource_available_time(pool, cal_map[pool].find_working_time(simulation_start_end[0],
                                                                                         simulation_start_end[1]))

    for i in pools_info.task_pools:
        if i in result[1].keys():
            total_cost = 0
            for resource in pools_info.task_pools[i]:
                total_cost += resource['cost_per_hour']
            total_cost = total_cost / len(pools_info.task_pools[i])
            simulation_info.add_task_statistics(pools_info.task_pools, i, float(result[1][i].waiting_time.avg),
                                                float(result[1][i].duration.avg),
                                                total_cost)
        else:
            total_cost = 0
            for resource in pools_info.task_pools[i]:
                total_cost += resource['cost_per_hour']
            total_cost = total_cost / len(pools_info.task_pools[i])
            simulation_info.add_task_statistics(pools_info.task_pools, i,
                                                float(0.0),
                                                float(0.0),
                                                total_cost)
    simulation_info.mean_process_cycle_time = float(result[0].cycle_time.avg)

    # for i in result[2].keys():
    #     simulation_info.update_resource_utilization(result[2][i].r_profile.resource_id, result[2][i].utilization)
    #     simulation_info.update_resource_available_time(result[2][i].r_profile.resource_id, result[2][i].available_time)
    # for i in result[1].keys():
    #     total_cost = 0
    #     for resource in pools_info.task_pools[i]:
    #         total_cost += resource['cost_per_hour']
    #     total_cost = total_cost / len(pools_info.task_pools[i])
    #     simulation_info.add_task_statistics(pools_info.task_pools, i, float(result[1][i].waiting_time.avg),
    #                                         float(result[1][i].duration.avg),
    #                                         total_cost)
    # simulation_info.mean_process_cycle_time = float(result[0].cycle_time.avg)

    return simulation_info, traces


def perform_simulations(pools_info,
                        log_name,
                        solution_index,
                        json_path,
                        model_file_path=temp_bpmn_file,
                        stat_out_path="./output_files/bimp_temp_files/output.csv",
                        starting_at=None):
    print("Running Simulation for Solution # %d (ID: %s) ..." % (solution_index, pools_info.id))
    # simulated_info = load_simulation_result(log_name, pools_info)
    parallel_start_time = time.time()
    # TODO Where to find traces if sim_info is not None
    # if simulated_info is not None:
    #     pool = multiprocessing.Pool(10)
    #     async_results = [pool.apply_async(process_simulations, (model_file_path, json_path, 1500, pools_info)) for i in
    #                      range(simulations_count)]
    #     traces = [ar.get()[1] for ar in async_results]
    #     pool.close()
    #     pool.join()
    #
    #     return simulated_info, traces

    # SEQUENTIAL RUN -

    s_res_list = []
    traces_list = []
    for i in range(3):
        s_res, traces = process_simulations(model_file_path, json_path, 550, pools_info)
        s_res_list.append(s_res)
        traces_list.append(traces)

    return estimate_median_absolute_deviation(pools_info, log_name, s_res_list, parallel_start_time), traces_list

    # MULTIPROCESSING RUN -
    # Multiprocessing used to reduce total processing time, dependent on # cores in system
    # pool = multiprocessing.Pool(4)
    # async_results = [pool.apply_async(process_simulations, (model_file_path, json_path, 550, pools_info)) for i in
    #                  range(5)]
    # simulation_results = [ar.get()[0] for ar in async_results]
    # traces = [ar.get()[1] for ar in async_results]
    # pool.close()
    # pool.join()

    # return estimate_median_absolute_deviation(pools_info, log_name, simulation_results, parallel_start_time), traces


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
    print("Simulation Average Time: %s" % str(datetime.timedelta(seconds=(total_time / 5))))
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
