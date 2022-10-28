from new_version.pareto_algorithms_and_metrics.hill_climb import hill_climb
from new_version.pareto_algorithms_and_metrics.pareto_metrics import GlobalParetoMetrics
from new_version.support_modules.plot_statistics_handler import print_solution_statistics

to_execute = {'HC-STRICT': False,
              'HC-FLEX': False,
              'TS-STRICT': False,
              'NSGA-II': False,
              'METRICS': True}

if __name__ == "__main__":
    log_name = "DEFAULT"
    xes_path = "./test_assets/log_demo_filtered_opt.xes"
    bpmn_path = "./test_assets/credit_application_diff.bpmn"
    timetable_path = "./test_assets/credit_application_diff.json"
    constraints_path = "./test_assets/constraints.json"
    max_func_ev = 10000
    non_opt_ratio = 0.08
    tot_simulations = 15

    if to_execute['HC-STRICT']:
        hill_climb(log_name, xes_path, bpmn_path, timetable_path, constraints_path, max_func_ev, non_opt_ratio, tot_simulations, False)
    if to_execute['METRICS']:
        metrics = GlobalParetoMetrics(log_name, ['hill_clmb_without_mad', 'hill_clmb_with_mad', 'tabu_srch_without_mad',
                                                 'nsga2'])
        print_solution_statistics(metrics, log_name)
