import os

from new_version.pareto_algorithms_and_metrics.hill_climb import hill_climb
from new_version.pareto_algorithms_and_metrics.pareto_metrics import GlobalParetoMetrics
from new_version.support_modules.plot_statistics_handler import print_solution_statistics

to_execute = {'HC-STRICT': True,
              'HC-FLEX': False,
              'TS-STRICT': False,
              'NSGA-II': False,
              'METRICS': False}


# log_name = "PRODUCTION"
# bpmn_path = "./test_assets/production/Production.bpmn"
# timetable_path = "./test_assets/production/sim_json.json"
# constraints_path = "./test_assets/production/constraints.json"

def execute_algorithm_variants(only_calendar):
    # log_name = "DEFAULT"
    # xes_path = "./test_assets/log_demo_filtered_opt.xes"
    # bpmn_path = "./test_assets/credit_application_diff.bpmn"
    # timetable_path = "./test_assets/credit_application_diff.json"
    # constraints_path = "./test_assets/constraints.json"
    log_name = "PRODUCTION"
    # log_name = "PRODUCTION_ONLY_CALENDAR"
    bpmn_path = "./test_assets/production/Production.bpmn"
    timetable_path = "./test_assets/production/sim_json.json"
    constraints_path = "./test_assets/production/constraints.json"

    max_func_ev = 10000
    non_opt_ratio = 0.08
    tot_simulations = 5

    if to_execute['HC-STRICT']:
        hill_climb(log_name, bpmn_path, timetable_path, constraints_path, max_func_ev, non_opt_ratio,
                   tot_simulations, False, False,  only_calendar)
    if to_execute['HC-FLEX']:
        hill_climb(log_name, bpmn_path, timetable_path, constraints_path, max_func_ev, non_opt_ratio,
                   tot_simulations, False, True, only_calendar)
    if to_execute['TS-STRICT']:
        hill_climb(log_name, bpmn_path, timetable_path, constraints_path, max_func_ev, non_opt_ratio,
                   tot_simulations, True, False, only_calendar)
    if to_execute['METRICS']:
        metrics = GlobalParetoMetrics(log_name, ['hill_clmb_without_mad', 'hill_clmb_with_mad', 'tabu_srch_without_mad', 'hill_clmb_without_mad_orlenys',
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
    execute_algorithm_variants(False)
    os._exit(0)


if __name__ == "__main__":
    main()
