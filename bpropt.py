import os

from pareto_algorithms_and_metrics.pareto_metrics import GlobalParetoMetrics
from support_modules.file_manager import xes_simodbpmn_file_paths

from pareto_algorithms_and_metrics.alg_hill_climb_tabu_search import refined_hill_pareto
from pareto_algorithms_and_metrics.alg_genetic_nsga2 import nsga2_genetic
from support_modules.plot_statistics_handler import print_solution_statistics

to_execute = {'HC-STRICT': False,
              'HC-FLEX': False,
              'TS-STRICT': False,
              'NSGA-II': False,
              'METRICS': True}

experiment_logs = {0: 'production',
                   1: 'purchasing_example',
                   2: 'consulta_data_mining',
                   3: 'insurance',
                   4: 'call_centre',
                   5: 'bpi_challenge_2012',
                   6: 'bpi_challenge_2017_filtered',
                   7: 'bpi_challenge_2017'}


def execute_algorithm_variants(process_index, xes_path, max_func_ev, non_opt_ratio, tot_simulations, bpmn_path, json_path):
    log_name = experiment_logs[process_index]
    # xes_path = xes_simodbpmn_file_paths[log_name][0]
    # bpmn_path = xes_simodbpmn_file_paths[log_name][1]
    xes_path = xes_path
    json_path = json_path
    bpmn_path = bpmn_path
    if to_execute['HC-STRICT']:
        # Executing Hill-Climbing without Median Absolute Deviation (HC-STRICT)
        refined_hill_pareto(log_name, xes_path, bpmn_path, max_func_ev, non_opt_ratio, tot_simulations, False, False)
    if to_execute['HC-FLEX']:
        # Executing Hill-Climbing with Median Absolute Deviation (HC-FLEX)
        refined_hill_pareto(log_name, xes_path, bpmn_path, max_func_ev, non_opt_ratio, tot_simulations, False, True)
    if to_execute['TS-STRICT']:
        # Executing Tabu-Search without Median Absolute Deviation (TS-STRICT)
        refined_hill_pareto(log_name, xes_path, bpmn_path, max_func_ev, non_opt_ratio, tot_simulations, True, False)
    if to_execute['NSGA-II']:
        # Executing Genetic Algorithm NSGA-II without Median Absolute Deviation
        nsga2_genetic(log_name, xes_path, bpmn_path, max_func_ev / 40, tot_simulations, json_path)
    if to_execute['METRICS']:
        metrics = GlobalParetoMetrics(log_name, ['hill_clmb_without_mad', 'hill_clmb_with_mad', 'tabu_srch_without_mad',
                                                 'nsga2'])
        print_solution_statistics(metrics, log_name)


def main():
    # Uncomment to execute the algorithms on all the available process  ...
    # for log_index in range(0, len(experiment_logs)):
    #     execute_algorithm_variants(log_index, 10000, 0.08, 15)

    # 1st Parameter: Index of the process to optimize -- from list experiment_logs
    # 2nd Parameter: Max Number of function evaluations (i.e. resource allocations to assess through simulation)
    # 3rd Parameter: Max Number (ratio) of function evaluations without discovering a Pareto-optimal solution
    # 4th Parameter: Number of simulations to perform per resource allocation
    execute_algorithm_variants(0, './test_assets/log_demo_filtered_opt.xes', 10000, 0.08, 100, './test_assets/Credit Application Simulation.bpmn', './test_assets/demo_filtered_opt.json')
    os._exit(0)


if __name__ == "__main__":
    main()
