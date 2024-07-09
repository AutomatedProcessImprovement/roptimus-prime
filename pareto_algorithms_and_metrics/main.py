import json
import os
import shutil
import tempfile
import time
from typing import Optional

from data_structures.iteration_info import IterationInfo
from data_structures.solution_json_output import FullOutputJson, iteration_info_to_solution
from pareto_algorithms_and_metrics.hill_climb import Cancelable, IterationCallbackType, hill_climb
from pareto_algorithms_and_metrics.pareto_metrics import GlobalParetoMetrics
from support_modules.file_manager import SOLUTIONS_FOLDER, TMP_FOLDER, BPM_DEMO_FOLDER, initialize_files, \
    reset_after_each_execution, demo_file_path
from support_modules.plot_statistics_handler import print_solution_statistics, return_api_solution_statistics, \
    return_api_solution_statistics_json

# from test_assets.experiments.experiment_setup import experiments_file_paths, experiments

TO_EXECUTE = {'HC-STRICT': False,
              'HC-FLEX': False,
              'TS-STRICT': False,
              'NSGA-II': False,
              'METRICS': True}

APPROACHES = {"only_calendar": True,  # Only perform optimization on schedule level
              "only_add_remove": False,  # Only perform optimization on resource level
              "combined": False,  # Combine schedule + resource optimization -> (WT/Cost/IT | Add/Remove) in 1 iteration
              "first_calendar_then_add_remove": False,  # Only calendar until No_improvement found, then add/remove
              "first_add_remove_then_calendar": False  # Only add/remove until No_improvement found, then calendar
              }


# def execute_algorithm_variants(log_index, to_execute, approaches):
#     log_name = experiments[log_index]
#     timetable_path = experiments_file_paths[log_name][0]
#     constraints_path = experiments_file_paths[log_name][1]
#     bpmn_path = experiments_file_paths[log_name][2]

#     max_func_ev = 100
#     non_opt_ratio = 0.1
#     tot_simulations = 5

#     # Reset files just in case
#     # reset_after_each_execution(log_name)

#     print(log_name)
#     print(timetable_path)
#     print(constraints_path)
#     print(bpmn_path)
#     save_path = "../test_assets/experiments"

#     for approach in approaches:
#         if approaches[approach]:
#             if to_execute['HC-STRICT']:
#                 hill_climb(log_name, bpmn_path, timetable_path, constraints_path, max_func_ev, non_opt_ratio,
#                            False, False, approach)
#                 reset_after_each_execution(os.path.join(save_path, log_name))
#             if to_execute['HC-FLEX']:
#                 hill_climb(log_name, bpmn_path, timetable_path, constraints_path, max_func_ev, non_opt_ratio,
#                            False, True, approach)
#                 reset_after_each_execution(os.path.join(save_path, log_name))

#     # if approaches['only_calendar'] and not approaches['first_calendar_then_add_remove']:
#     #     if to_execute['HC-STRICT']:
#     #         hill_climb(log_name, bpmn_path, timetable_path, constraints_path, max_func_ev, non_opt_ratio,
#     #                    False, False, 'only_calendar')
#     #         reset_after_each_execution(os.path.join(save_path, log_name))
#     #     if to_execute['HC-FLEX']:
#     #         hill_climb(log_name, bpmn_path, timetable_path, constraints_path, max_func_ev, non_opt_ratio,
#     #                    False, True, 'only_calendar')
#     #         reset_after_each_execution(os.path.join(save_path, log_name))
#     # if approaches['only_add_remove'] and not approaches['first_add_remove_then_calendar']:
#     #     if to_execute['HC-STRICT']:
#     #         hill_climb(log_name, bpmn_path, timetable_path, constraints_path, max_func_ev, non_opt_ratio,
#     #                    False, False, 'only_add_remove')
#     #         reset_after_each_execution(os.path.join(save_path, log_name))
#     #     if to_execute['HC-FLEX']:
#     #         hill_climb(log_name, bpmn_path, timetable_path, constraints_path, max_func_ev, non_opt_ratio,
#     #                    False, True, 'only_add_remove')
#     #         reset_after_each_execution(os.path.join(save_path, log_name))
#     # if approaches['combined']:
#     #     if to_execute['HC-STRICT']:
#     #         hill_climb(log_name, bpmn_path, timetable_path, constraints_path, max_func_ev, non_opt_ratio,
#     #                    False, False, 'combined')
#     #         reset_after_each_execution(os.path.join(save_path, log_name))
#     #     if to_execute['HC-FLEX']:
#     #         hill_climb(log_name, bpmn_path, timetable_path, constraints_path, max_func_ev, non_opt_ratio,
#     #                    False, True, 'combined')
#     #         reset_after_each_execution(os.path.join(save_path, log_name))
#     # if approaches['first_calendar_then_add_remove']:
#     #     if to_execute['HC-STRICT']:
#     #         hill_climb(log_name, bpmn_path, timetable_path, constraints_path, max_func_ev, non_opt_ratio,
#     #                    False, False, 'first_calendar_then_add_remove')
#     #         reset_after_each_execution(os.path.join(save_path, log_name))
#     #     if to_execute['HC-FLEX']:
#     #         hill_climb(log_name, bpmn_path, timetable_path, constraints_path, max_func_ev, non_opt_ratio,
#     #                    False, True, 'first_calendar_then_add_remove')
#     #         reset_after_each_execution(os.path.join(save_path, log_name))
#     # if approaches['first_add_remove_then_calendar']:
#     #     if to_execute['HC-STRICT']:
#     #         hill_climb(log_name, bpmn_path, timetable_path, constraints_path, max_func_ev, non_opt_ratio,
#     #                    False, False, 'first_add_remove_then_calendar')
#     #         reset_after_each_execution(os.path.join(save_path, log_name))
#     #     if to_execute['HC-FLEX']:
#     #         hill_climb(log_name, bpmn_path, timetable_path, constraints_path, max_func_ev, non_opt_ratio,
#     #                    False, True, 'first_add_remove_then_calendar')
#     #         reset_after_each_execution(os.path.join(save_path, log_name))

#     if to_execute['METRICS']:
#         metrics = GlobalParetoMetrics(log_name, ['hill_clmb_combined_without_mad',
#                                                  'hill_clmb_combined_with_mad',

#                                                  'hill_clmb_only_calendar_without_mad',
#                                                  'hill_clmb_only_calendar_with_mad',

#                                                  'hill_clmb_only_add_remove_without_mad',
#                                                  'hill_clmb_only_add_remove_with_mad',

#                                                  'hill_clmb_first_calendar_then_add_remove_without_mad',
#                                                  'hill_clmb_first_calendar_then_add_remove_with_mad',

#                                                  'hill_clmb_first_add_remove_then_calendar_without_mad',
#                                                  'hill_clmb_first_add_remove_then_calendar_with_mad',
#                                                  ])
#         print_solution_statistics(metrics, log_name)


def run_optimization(bpmn_path, sim_params_path, constraints_path, total_iterations, algorithm, approach,
                     stat_out_path: str, log_name: str, iteration_callback: IterationCallbackType = None,
                     processing_request: Cancelable = Cancelable()) -> Optional[FullOutputJson]:
    # Before running algortihm, clean up temp_files in ./json_files | ./temp_files

    # TODO
    #  - Path where to make copy of original files
    #  - Path where to write results

    to_execute = {'HC-STRICT': False,
                  'HC-FLEX': False,
                  'METRICS': True}

    approaches = {"only_calendar": False,  # Only perform optimization on schedule level
                  "only_add_remove": False,  # Only perform optimization on resource level
                  "combined": False,  # schedule + resource optimization -> (WT/Cost/IT | Add/Remove) in 1 iteration
                  "first_calendar_then_add_remove": False,  # Only calendar until No_improvement found, then add/remove
                  "first_add_remove_then_calendar": False  # Only add/remove until No_improvement found, then calendar
                  }

    # Either FLEX or STRICT
    if algorithm == 'HC-FLEX':
        to_execute['HC-FLEX'] = True
    if algorithm == 'HC-STRICT':
        to_execute['HC-STRICT'] = True

    # Select chosen approaches to execute
    if approach == "ALL":
        for key in approaches.keys():
            approaches[key] = True
    else:
        if approach == "CA":
            approaches['only_calendar'] = True
        if approach == "AR":
            approaches['only_add_remove'] = True
        if approach == "CO":
            approaches['combined'] = True
        if approach == "CAAR":
            approaches['first_calendar_then_add_remove'] = True
        if approach == "ARCA":
            approaches['first_add_remove_then_calendar'] = True

    max_func_ev = int(total_iterations)

    # Could also be parameterized
    non_opt_ratio = 0.1

    # Needs a parameter as well
    log_name = log_name

    # Path where to save copies of original cons/simparams
    save_path = os.path.join(TMP_FOLDER, str(time.time()))

    print("Running optimization for: " + log_name)
    print("Save path: " + save_path)

    try:
        initialize_files(save_path, bpmn_path, sim_params_path, constraints_path)
    except Exception:
        print("Oh no")

    tmp_bpmn_path = os.path.join(save_path, "model.bpmn")
    tmp_timetable_path = os.path.join(save_path, "timetable.json")
    tmp_constraints_path = os.path.join(save_path, "constraints.json")

    solutions_iteration_infos_per_approach: dict[str, list[IterationInfo]] = {}
    if approaches['only_calendar'] and not approaches['first_calendar_then_add_remove']:
        if to_execute['HC-STRICT'] and not processing_request.should_be_cancelled:
            it_infos = hill_climb(log_name, tmp_bpmn_path, tmp_timetable_path, tmp_constraints_path, max_func_ev,
                                  non_opt_ratio,
                                  False, False, 'only_calendar', iteration_callback, processing_request)
            solutions_iteration_infos_per_approach['only_calendar_without_mad'] = (it_infos or [])
            reset_after_each_execution(save_path)
        if to_execute['HC-FLEX'] and not processing_request.should_be_cancelled:
            it_infos = hill_climb(log_name, tmp_bpmn_path, tmp_timetable_path, tmp_constraints_path, max_func_ev,
                                  non_opt_ratio,
                                  False, True, 'only_calendar', iteration_callback, processing_request)
            solutions_iteration_infos_per_approach['only_calendar_with_mad'] = (it_infos or [])
            reset_after_each_execution(save_path)
    if approaches['only_add_remove'] and not approaches['first_add_remove_then_calendar']:
        if to_execute['HC-STRICT'] and not processing_request.should_be_cancelled:
            it_infos = hill_climb(log_name, tmp_bpmn_path, tmp_timetable_path, tmp_constraints_path, max_func_ev,
                                  non_opt_ratio,
                                  False, False, 'only_add_remove', iteration_callback, processing_request)
            solutions_iteration_infos_per_approach['only_add_remove_without_mad'] = (it_infos or [])
            reset_after_each_execution(save_path)
        if to_execute['HC-FLEX'] and not processing_request.should_be_cancelled:
            it_infos = hill_climb(log_name, tmp_bpmn_path, tmp_timetable_path, tmp_constraints_path, max_func_ev,
                                  non_opt_ratio,
                                  False, True, 'only_add_remove', iteration_callback, processing_request)
            solutions_iteration_infos_per_approach['only_add_remove_with_mad'] = (it_infos or [])
            reset_after_each_execution(save_path)
    if approaches['combined']:
        if to_execute['HC-STRICT'] and not processing_request.should_be_cancelled:
            it_infos = hill_climb(log_name, tmp_bpmn_path, tmp_timetable_path, tmp_constraints_path, max_func_ev,
                                  non_opt_ratio,
                                  False, False, 'combined', iteration_callback, processing_request)
            solutions_iteration_infos_per_approach['combined_without_mad'] = (it_infos or [])
            reset_after_each_execution(save_path)
        if to_execute['HC-FLEX'] and not processing_request.should_be_cancelled:
            it_infos = hill_climb(log_name, tmp_bpmn_path, tmp_timetable_path, tmp_constraints_path, max_func_ev,
                                  non_opt_ratio,
                                  False, True, 'combined', iteration_callback, processing_request)
            solutions_iteration_infos_per_approach['combined_with_mad'] = (it_infos or [])
            reset_after_each_execution(save_path)
    if approaches['first_calendar_then_add_remove']:
        if to_execute['HC-STRICT'] and not processing_request.should_be_cancelled:
            it_infos = hill_climb(log_name, tmp_bpmn_path, tmp_timetable_path, tmp_constraints_path, max_func_ev,
                                  non_opt_ratio,
                                  False, False, 'first_calendar_then_add_remove', iteration_callback,
                                  processing_request)
            solutions_iteration_infos_per_approach['first_calendar_then_add_remove_without_mad'] = (it_infos or [])
            reset_after_each_execution(save_path)
        if to_execute['HC-FLEX'] and not processing_request.should_be_cancelled:
            it_infos = hill_climb(log_name, tmp_bpmn_path, tmp_timetable_path, tmp_constraints_path, max_func_ev,
                                  non_opt_ratio,
                                  False, True, 'first_calendar_then_add_remove', iteration_callback, processing_request)
            solutions_iteration_infos_per_approach['first_calendar_then_add_remove_with_mad'] = (it_infos or [])
            reset_after_each_execution(save_path)
    if approaches['first_add_remove_then_calendar']:
        if to_execute['HC-STRICT'] and not processing_request.should_be_cancelled:
            it_infos = hill_climb(log_name, tmp_bpmn_path, tmp_timetable_path, tmp_constraints_path, max_func_ev,
                                  non_opt_ratio,
                                  False, False, 'first_add_remove_then_calendar', iteration_callback,
                                  processing_request)
            solutions_iteration_infos_per_approach['first_add_remove_then_calendar_without_mad'] = (it_infos or [])
            reset_after_each_execution(save_path)
        if to_execute['HC-FLEX'] and not processing_request.should_be_cancelled:
            it_infos = hill_climb(log_name, tmp_bpmn_path, tmp_timetable_path, tmp_constraints_path, max_func_ev,
                                  non_opt_ratio,
                                  False, True, 'first_add_remove_then_calendar', iteration_callback, processing_request)
            solutions_iteration_infos_per_approach['first_add_remove_then_calendar_with_mad'] = (it_infos or [])
            reset_after_each_execution(save_path)

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
        solutions_iteration_infos = [(approach, info) for (approach, infos) in
                                     solutions_iteration_infos_per_approach.items() for info in infos]
        solution_outputs = list(map(iteration_info_to_solution, solutions_iteration_infos))
        valid_solution_outputs = [x for x in solution_outputs if x is not None]
        output = FullOutputJson(
            name=log_name,
            initial_solution=next(
                iteration_info_to_solution(x) for x in solutions_iteration_infos if x[1].it_number == 0),
            final_solutions=valid_solution_outputs,
            current_solution=None,
            final_solution_metrics=return_api_solution_statistics(metrics, log_name)
        )
        # TODO: Correctly Clear Output files
        # path = SOLUTIONS_FOLDER
        # for _dir in os.listdir(path):
        #     if _dir == '.DS_Store':
        #         continue
        #     if _dir != 'ids.txt':
        #         shutil.rmtree(os.path.abspath(os.path.join(path, _dir)), ignore_errors=False, onerror=None)

        with open(stat_out_path, mode='w') as stat_file:
            stat_file.write(json.dumps(output, default=lambda x: x.to_json() if hasattr(x, 'to_json') else x.__dict__))

        return output

        # with open(save_path+"\\results.json", 'w') as o:
        #     o.write(output)

        # Remove all files in json_files for next task:

        # return os.path.abspath(os.path.join(save_path, 'results.json')), output

    return None


def main():
    # Uncomment to execute the algorithms on all the available process  ...
    # for log_index in range(0, len(experiment_logs)):
    #     execute_algorithm_variants(log_index, 10000, 0.08, 15)

    # for log_index in range(0, len(experiments)):
    #     execute_algorithm_variants(log_index, TO_EXECUTE, APPROACHES)

    # 1st Parameter: Index of the process to optimize -- from list experiment_logs
    # 2nd Parameter: Max Number of function evaluations (i.e. resource allocations to assess through simulation)
    # 3rd Parameter: Max Number (ratio) of function evaluations without discovering a Pareto-optimal solution
    # 4th Parameter: Number of simulations to perform per resource allocation
    # execute_algorithm_variants(7, TO_EXECUTE, APPROACHES)

    # run_optimization(bpmn_path, sim_params_path, constraints_path, total_iterations, algorithm, approach,
    #                stat_out_path: str, log_name: str, iteration_callback: IterationCallbackType = None, processing_request: Cancelable = Cancelable()) ->
    #Optional[FullOutputJson]

    run_optimization(bpmn_path=demo_file_path("LoanModel.bpmn"),
                     sim_params_path=demo_file_path("Timetable.json"),
                     constraints_path=demo_file_path("Constraints.json"),
                     total_iterations=100,
                     algorithm="HC-STRICT",
                     approach="CO",
                     stat_out_path="demo_stats.txt",
                     log_name="bpm_demo")
    os._exit(0)


if __name__ == "__main__":
    main()
