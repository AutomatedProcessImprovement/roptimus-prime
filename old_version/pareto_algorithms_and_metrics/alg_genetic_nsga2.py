import time
import datetime
from shutil import copyfile
from new_version.data_structures.nsga2_problem import NSGA2Problem
from pymoo.optimize import minimize

from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.sampling.rnd import IntegerRandomSampling
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PolynomialMutation

from new_version.pareto_algorithms_and_metrics.alg_hill_climb_tabu_search import set_up_cost
from new_version.pareto_algorithms_and_metrics.pareto_metrics import AlgorithmResults
from new_version.support_modules.file_manager import temp_bpmn_file, create_genetic_stats_files, read_stats_file
from new_version.support_modules.log_parser import extract_data_from_xes_event_log


def nsga2_genetic(log_name, xes_path, bpmn_path, max_iterations, total_simulations, json_path, cost_type=1):
    copyfile(bpmn_path, temp_bpmn_file)
    create_genetic_stats_files(log_name)
    starting_time = time.time()

    xes_log_info = extract_data_from_xes_event_log(xes_path)
    initial_pools_info = set_up_cost(cost_type, xes_log_info)

    resource_opt_problem = NSGA2Problem(log_name, initial_pools_info, total_simulations, json_path=json_path)
    algorithm = NSGA2(pop_size=40,
                      sampling=IntegerRandomSampling(),
                      crossover=SBX(prob=0.9, eta=15),
                      mutation=PolynomialMutation(prob=1.0, eta=20),
                      eliminate_duplicates=True)

    minimize(resource_opt_problem,
             algorithm,
             ('n_gen', max_iterations),
             seed=1,
             pf=resource_opt_problem.pareto_front(use_cache=False),
             save_history=False,
             verbose=False)

    print("Algortithm NSGA-II Completed")
    print("Process Name: %s" % log_name)
    print("Total time (sec): ............ %s " % str(datetime.timedelta(seconds=(time.time() - starting_time))))
    print("Function Eval Performed: ..... %d" % resource_opt_problem.it_number)
    tot_generations = int(resource_opt_problem.it_number / 40) + (1 if resource_opt_problem.it_number % 40 > 0 else 0)
    print("Generations Explored: ........ %d" % tot_generations)
    execution_info = read_stats_file(log_name, 'nsga2')
    alg_info = AlgorithmResults(execution_info, False)
    print("Discovered Pareto Size: ...... %d" % len(alg_info.pareto_front))
    print("---------------------------------------------------")
