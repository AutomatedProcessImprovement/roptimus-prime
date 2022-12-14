import os

from new_version.pareto_algorithms_and_metrics.hill_climb import hill_climb
from new_version.pareto_algorithms_and_metrics.pareto_metrics import GlobalParetoMetrics
from new_version.support_modules.plot_statistics_handler import print_solution_statistics
from new_version.test_assets.experiments.experiment_setup import experiments_file_paths, experiments, \
    reset_after_each_execution

to_execute = {'HC-STRICT': False,
              'HC-FLEX': False,
              'TS-STRICT': False,
              'NSGA-II': False,
              'METRICS': True}

APPROACHES = {"only_calendar": True,  # Only perform optimization on schedule level
              "only_add_remove": True,  # Only perform optimization on resource level
              "combined": True,  # Combine schedule + resource optimization -> (WT/Cost/IT | Add/Remove) in 1 iteration
              "first_calendar_then_add_remove": True,  # Only calendar until No_improvement found, then add/remove
              "first_add_remove_then_calendar": True  # Only add/remove until No_improvement found, then calendar
              }


def execute_algorithm_variants(log_index):

    log_name = experiments[log_index]
    timetable_path = experiments_file_paths[log_name][0]
    constraints_path = experiments_file_paths[log_name][1]
    bpmn_path = experiments_file_paths[log_name][2]

    print(log_name)

    max_func_ev = 5000
    non_opt_ratio = 0.1
    tot_simulations = 5

    # Reset files just in case
    reset_after_each_execution(log_name)

    if APPROACHES['only_calendar'] and not APPROACHES['first_calendar_then_add_remove']:
        if to_execute['HC-STRICT']:
            hill_climb(log_name, bpmn_path, timetable_path, constraints_path, max_func_ev, non_opt_ratio,
                       False, False, 'only_calendar')
            reset_after_each_execution(log_name)
        if to_execute['HC-FLEX']:
            hill_climb(log_name, bpmn_path, timetable_path, constraints_path, max_func_ev, non_opt_ratio,
                       False, True, 'only_calendar')
            reset_after_each_execution(log_name)
    if APPROACHES['only_add_remove'] and not APPROACHES['first_add_remove_then_calendar']:
        if to_execute['HC-STRICT']:
            hill_climb(log_name, bpmn_path, timetable_path, constraints_path, max_func_ev, non_opt_ratio,
                       False, False, 'only_add_remove')
            reset_after_each_execution(log_name)
        if to_execute['HC-FLEX']:
            hill_climb(log_name, bpmn_path, timetable_path, constraints_path, max_func_ev, non_opt_ratio,
                       False, True, 'only_add_remove')
            reset_after_each_execution(log_name)
    if APPROACHES['combined']:
        if to_execute['HC-STRICT']:
            hill_climb(log_name, bpmn_path, timetable_path, constraints_path, max_func_ev, non_opt_ratio,
                       False, False, 'combined')
            reset_after_each_execution(log_name)
        if to_execute['HC-FLEX']:
            hill_climb(log_name, bpmn_path, timetable_path, constraints_path, max_func_ev, non_opt_ratio,
                       False, True, 'combined')
            reset_after_each_execution(log_name)
    if APPROACHES['first_calendar_then_add_remove']:
        if to_execute['HC-STRICT']:
            hill_climb(log_name, bpmn_path, timetable_path, constraints_path, max_func_ev, non_opt_ratio,
                       False, False, 'first_calendar_then_add_remove')
            reset_after_each_execution(log_name)
        if to_execute['HC-FLEX']:
            hill_climb(log_name, bpmn_path, timetable_path, constraints_path, max_func_ev, non_opt_ratio,
                       False, True, 'first_calendar_then_add_remove')
            reset_after_each_execution(log_name)
    if APPROACHES['first_add_remove_then_calendar']:
        if to_execute['HC-STRICT']:
            hill_climb(log_name, bpmn_path, timetable_path, constraints_path, max_func_ev, non_opt_ratio,
                       False, False, 'first_add_remove_then_calendar')
            reset_after_each_execution(log_name)
        if to_execute['HC-FLEX']:
            hill_climb(log_name, bpmn_path, timetable_path, constraints_path, max_func_ev, non_opt_ratio,
                       False, True, 'first_add_remove_then_calendar')
            reset_after_each_execution(log_name)

    if to_execute['METRICS']:
        metrics = GlobalParetoMetrics(log_name, ['hill_clmb_combined_without_mad',
                                                 'hill_clmb_combined_with_mad',

                                                 'hill_clmb_only_calendar_without_mad',
                                                 'hill_clmb_only_calendar_with_mad',

                                                 'hill_clmb_only_add_remove_without_mad',
                                                 'hill_clmb_only_add_remove_with_mad',

                                                 'hill_clmb_first_calendar_then_add_remove_without_mad',
                                                 'hill_clmb_first_calendar_then_add_remove_with_mad',

                                                 'hill_clmb_first_add_remove_then_calendar_without_mad',
                                                 'hill_clmb_first_add_remove_then_calendar_with_mad',
                                                 ])
        print_solution_statistics(metrics, log_name)


def main():
    # Uncomment to execute the algorithms on all the available process  ...
    # for log_index in range(0, len(experiment_logs)):
    #     execute_algorithm_variants(log_index, 10000, 0.08, 15)

    for log_index in range(0, len(experiments)):
        execute_algorithm_variants(log_index)

    # 1st Parameter: Index of the process to optimize -- from list experiment_logs
    # 2nd Parameter: Max Number of function evaluations (i.e. resource allocations to assess through simulation)
    # 3rd Parameter: Max Number (ratio) of function evaluations without discovering a Pareto-optimal solution
    # 4th Parameter: Number of simulations to perform per resource allocation
    # execute_algorithm_variants(0)
    os._exit(0)


if __name__ == "__main__":
    main()
