import json
import os
import datetime
from typing import Dict, TypedDict
import matplotlib.pyplot as plt

from data_structures.solution_space import SolutionOutputObject, SolutionOutputParetoValue
from pareto_algorithms_and_metrics.pareto_metrics import AlgorithmResults, GlobalParetoMetrics
from support_modules.file_manager import solutions_order_stats_file, EXPERIMENTS_PLOTS_PATH



def print_line(file_writer, to_print):
    print(to_print)
    file_writer.write(str(to_print) + '\n')


def setup_dir(log_name):
    file_path = "%s\\%s" % (EXPERIMENTS_PLOTS_PATH, log_name)
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    return file_path + '\\'


def return_api_solution_statistics(p_metrics: GlobalParetoMetrics, log_name:str):
    f_eval = plot_data_profiles_microservice(p_metrics.algorithm_results, log_name, 0)

    t_f_eval = 0
    for a_name in f_eval:
        t_f_eval += f_eval[a_name]
    initial_metrics = None
    for v in p_metrics.algorithm_results.values():
        initial_metrics = v.explored_solutions.get(p_metrics.initial_solution)
        break
    assert initial_metrics is not None
    i_mct = initial_metrics.median_cycle_time
    i_mec = initial_metrics.median_execution_cost


    solution_objects: list[SolutionOutputObject] = []
    for alg in p_metrics.algorithm_results:
        [l_name, a_name] = extract_log_alg_name(alg)
        alg_res = p_metrics.algorithm_results[alg]

        [hyperarea_diff, hausdorff_dist, delta, purity] = p_metrics.compute_metrics(p_metrics.joint_pareto_info)
        [in_pareto, ave_time, ave_cost] = find_common_elements(p_metrics.joint_pareto_info, p_metrics.joint_pareto_info)

        time_metric = i_mct / ave_time
        cost_metric = i_mec / ave_cost
        general_info = (in_pareto, ave_time, ave_cost)
        metrics = (hyperarea_diff, hausdorff_dist, delta, purity)
        impr_index= (time_metric, cost_metric)

        out = save_allocation_statistics_into_SolutionObject(a_name,alg_res, t_f_eval,
                                                       general_info,
                                                       metrics,
                                                       impr_index)
        solution_objects.append(out)
    return solution_objects

def return_api_solution_statistics_json(p_metrics: GlobalParetoMetrics, log_name:str):
    solutions = return_api_solution_statistics(p_metrics, log_name)
    json_string = [ob.__dict__ for ob in solutions]

    return json_string


def return_solution_statistics(p_metrics, log_name):
    dir_path = setup_dir(log_name)
    file_writer = open(dir_path + "stats_summary.txt", 'w')

    joint_pareto = ['Joint Pareto Size (without MAD): %d --------------------------------------------------------'
                    % len(p_metrics.joint_pareto_info)]
    print_line(file_writer, joint_pareto)
    max_leng = len(log_name) + 14

    f_eval = plot_data_profiles_microservice(p_metrics.algorithm_results, log_name, 0)
    # plot_data_profiles(dir_path, p_metrics.algorithm_results, log_name, 1)
    t_f_eval = 0
    initial_metrics = None
    for v in p_metrics.algorithm_results.values():
        initial_metrics = v.explored_solutions.get(p_metrics.initial_solution)
        break

    assert initial_metrics is not None
    i_mct = initial_metrics.median_cycle_time
    i_mec = initial_metrics.median_execution_cost

    i_mct_mec = (i_mct, i_mec)
    for a_name in f_eval:
        t_f_eval += f_eval[a_name]
    print_line(file_writer, fill_str('Alg_Name', max_leng) + '  #_F_Ev  #_Sol  P_Size  In_JP  !JP  Hyperarea  '
                                                             'Hausdorff-Dist  Delta-Sprd  Purity-Rate  '
                                                             'Ave_Time                 Ave_cost'
                                                             '     Time Metric     Cost Metric')
    print_pareto_info(file_writer, p_metrics, 'initial (' + log_name + ')', 'initial', t_f_eval, max_leng,
                      p_metrics.joint_pareto_info, p_metrics.total_explored_solution, i_mct_mec)
    print_pareto_info(file_writer, p_metrics, 'joint_pareto(' + log_name + ')', 'joint', t_f_eval, max_leng,
                      p_metrics.joint_pareto_info, p_metrics.total_explored_solution, i_mct_mec)

    output_file_paths = []

    for alg_name in p_metrics.algorithm_results:
        [l_name, a_name] = extract_log_alg_name(alg_name)
        a_name = a_name
        output_file_paths.append(print_pareto_info(file_writer, p_metrics, a_name, alg_name, f_eval[alg_name], max_leng,
                                                   p_metrics.algorithm_results[alg_name].pareto_front,
                                                   len(p_metrics.algorithm_results[alg_name].explored_solutions),
                                                   i_mct_mec))
    print_line(file_writer, '------------------------------------------------------')

    return output_file_paths


def print_solution_statistics(p_metrics, log_name):
    dir_path = setup_dir(log_name)
    file_writer = open(dir_path + "stats_summary.txt", 'w')

    joint_pareto = ['Joint Pareto Size (without MAD): %d --------------------------------------------------------'
                    % len(p_metrics.joint_pareto_info)]
    print_line(file_writer, joint_pareto)
    max_leng = len(log_name) + 14

    f_eval = plot_data_profiles(dir_path, p_metrics.algorithm_results, log_name, 0)
    plot_data_profiles(dir_path, p_metrics.algorithm_results, log_name, 1)
    t_f_eval = 0
    initial_metrics = None
    for v in p_metrics.algorithm_results.values():
        initial_metrics = v.explored_solutions.get(p_metrics.initial_solution)
        break
    assert initial_metrics is not None
    i_mct = initial_metrics.median_cycle_time
    i_mec = initial_metrics.median_execution_cost

    i_mct_mec = (i_mct, i_mec)
    for a_name in f_eval:
        t_f_eval += f_eval[a_name]
    print_line(file_writer, fill_str('Alg_Name', max_leng) + '  #_F_Ev  #_Sol  P_Size  In_JP  !JP  Hyperarea  '
                                                             'Hausdorff-Dist  Delta-Sprd  Purity-Rate  '
                                                             'Ave_Time                 Ave_cost'
                                                             '     Time Metric     Cost Metric')
    print_pareto_info(file_writer, p_metrics, 'initial (' + log_name + ')', 'initial', t_f_eval, max_leng,
                      p_metrics.joint_pareto_info, p_metrics.total_explored_solution, i_mct_mec)
    print_pareto_info(file_writer, p_metrics, 'joint_pareto(' + log_name + ')', 'joint', t_f_eval, max_leng,
                      p_metrics.joint_pareto_info, p_metrics.total_explored_solution, i_mct_mec)
    for alg_name in p_metrics.algorithm_results:
        [l_name, a_name] = extract_log_alg_name(alg_name)
        a_name = a_name
        print_pareto_info(file_writer, p_metrics, a_name, alg_name, f_eval[alg_name], max_leng,
                          p_metrics.algorithm_results[alg_name].pareto_front,
                          len(p_metrics.algorithm_results[alg_name].explored_solutions), i_mct_mec)
    print_line(file_writer, '------------------------------------------------------')

    plot_pareto_front(dir_path, p_metrics.algorithm_results, p_metrics.joint_pareto_info)


def print_pareto_info(f_writer, p_metric, alg_name, full_name, funct_ev, max_len, pareto_front, total_explored,
                      i_mct_mec):
    [hyperarea_diff, hausdorff_dist, delta, purity] = p_metric.compute_metrics(pareto_front)
    [in_pareto, ave_time, ave_cost] = find_common_elements(pareto_front, p_metric.joint_pareto_info)
    [l_name, a_name] = extract_log_alg_name(full_name)

    cost_metric = i_mct_mec[1] / ave_cost
    time_metric = i_mct_mec[0] / ave_time
    file_path = "%s\\%s_%s.txt" % (EXPERIMENTS_PLOTS_PATH, l_name, a_name)
    if 'joint_pareto' not in alg_name and 'initial' not in full_name:
        save_allocation_statistics(file_path, p_metric.algorithm_results[full_name], funct_ev,
                                   [in_pareto, ave_time, ave_cost], [hyperarea_diff, hausdorff_dist, delta, purity])
    if 'initial' in full_name:
        print_line(f_writer, '%s  %s  %s  %s  %s  %s  %s  %s  %s  %s  %s  %s  %s  %s'
                   % (fill_str(alg_name, max_len),
                      fill_str(str("-"), 6),
                      fill_str(str("-"), 5),
                      fill_str(str("-"), 6),
                      fill_str(str("-"), 5),
                      fill_str(str("-"), 3),
                      fill_str(str("-"), 9),
                      fill_str(str("-"), 14),
                      fill_str(str("-"), 10),
                      fill_str(str("-"), 11),
                      fill_str(str(str(datetime.timedelta(seconds=i_mct_mec[0]))), 23),
                      fill_str(str(round(i_mct_mec[1], 2)), 11),
                      fill_str(str(round((i_mct_mec[0]) / (i_mct_mec[0]), 6)), 15),
                      fill_str(str(round((i_mct_mec[1]) / (i_mct_mec[1]), 6)), 11)
                      ))
    else:
        print_line(f_writer, '%s  %s  %s  %s  %s  %s  %s  %s  %s  %s  %s  %s  %s  %s'
                   % (fill_str(alg_name, max_len),
                      fill_str(str(funct_ev), 6),
                      fill_str(str(total_explored), 5),
                      fill_str(str(len(pareto_front)), 6),
                      fill_str(str(in_pareto), 5),
                      fill_str(str(len(pareto_front) - in_pareto), 3),
                      fill_str(str(round(hyperarea_diff, 6)), 9),
                      fill_str(str(round(hausdorff_dist, 2)), 14),
                      fill_str(str(round(delta, 6)), 10),
                      fill_str(str(round(purity, 6)), 11),
                      fill_str(str(str(datetime.timedelta(seconds=ave_time))), 23),
                      fill_str(str(round(ave_cost, 2)), 11),
                      fill_str(str(round(time_metric, 6)), 15),
                      fill_str(str(round(cost_metric, 6)), 11)
                      ))
    return file_path


def find_common_elements(pareto_front, joint_pareto_info) -> tuple[float,float,float]:
    in_pareto:float = 0
    tot_time:float = 0
    tot_cost:float = 0
    for sol_id in pareto_front:
        tot_time += pareto_front[sol_id].cycle_time()
        tot_cost += pareto_front[sol_id].execution_cost()
        if sol_id in joint_pareto_info:
            in_pareto += 1
    return (in_pareto,
            tot_time / len(pareto_front),
            tot_cost / len(pareto_front))


def plot_data_profiles_microservice(algorithm_results, log_name, data_type=0):
    func_eval: Dict[str, int] = dict()
    colors = ['y', 'r', 'b', 'g', 'k', 'm', '#2ca02c', '#8c564b']
    alg_c = 1
    name_files = ["data_profiles_evaluated_functions", "data_profiles_explored_solutions"]
    x_names = ["Function Evaluations", "Explored Solutions"]
    name_index = 0
    text_x = []
    for alg_name in algorithm_results:
        [log_name, alg_name_1] = extract_log_alg_name(alg_name)
        solution_list = \
            solutions_order_stats_file(log_name, alg_name if 'nsga' not in alg_name else alg_name + "_simulation_info")
        assert solution_list is not None
        pareto_front = algorithm_results[alg_name].pareto_front
        if data_type == 1:
            not_repeated_sol = set()
            expl_sol = list()
            for sol_id in solution_list:
                if sol_id not in not_repeated_sol:
                    expl_sol.append(sol_id)
                    not_repeated_sol.add(sol_id)
            name_index = 1
            solution_list = expl_sol
        found_last = False
        current_pareto = set()
        x_axis = []
        y_axis = []
        i = 0
        for sol_id in solution_list:
            if sol_id in pareto_front:
                current_pareto.add(sol_id)
            x_axis.append(i)
            # if not found_last and len(current_pareto) == len(pareto_front):
            #     text_x.append(i)
            #     plt.plot(i, 1, color=colors[alg_c], marker='o')
            #     plt.axvline(x=i, color=colors[alg_c], linestyle='dotted')
            #     found_last = True
            y_axis.append(len(current_pareto) / len(pareto_front))
            i += 1
        func_eval[alg_name] = len(x_axis)
        # plt.plot(x_axis, y_axis, color=colors[alg_c], label=alg_name_1)
        alg_c += 1
    # plt.legend(framealpha=1, frameon=True)
    # plt.title('%s' % log_name)
    # plt.ylabel('Pareto Progress')
    # plt.xlabel(x_names[name_index])
    # plt.savefig("%s%s.pdf" % (file_path, name_files[name_index]))
    # plt.show()
    return func_eval


def plot_data_profiles(file_path, algorithm_results, log_name, data_type=0):
    func_eval = dict()
    colors = ['y', 'r', 'b', 'g', 'k', 'm', '#2ca02c', '#8c564b']
    alg_c = 1
    name_files = ["data_profiles_evaluated_functions", "data_profiles_explored_solutions"]
    x_names = ["Function Evaluations", "Explored Solutions"]
    name_index = 0
    text_x = []
    for alg_name in algorithm_results:
        [log_name, alg_name_1] = extract_log_alg_name(alg_name)
        solution_list = \
            solutions_order_stats_file(log_name, alg_name if 'nsga' not in alg_name else alg_name + "_simulation_info")
        assert solution_list is not None
        pareto_front = algorithm_results[alg_name].pareto_front
        if data_type == 1:
            not_repeated_sol = set()
            expl_sol = list()
            for sol_id in solution_list:
                if sol_id not in not_repeated_sol:
                    expl_sol.append(sol_id)
                    not_repeated_sol.add(sol_id)
            name_index = 1
            solution_list = expl_sol
        found_last = False
        current_pareto = set()
        x_axis = []
        y_axis = []
        i = 0
        for sol_id in solution_list:
            if sol_id in pareto_front:
                current_pareto.add(sol_id)
            x_axis.append(i)
            if not found_last and len(current_pareto) == len(pareto_front):
                text_x.append(i)
                plt.plot(i, 1, color=colors[alg_c], marker='o')
                plt.axvline(x=i, color=colors[alg_c], linestyle='dotted')
                found_last = True
            y_axis.append(len(current_pareto) / len(pareto_front))
            i += 1
        func_eval[alg_name] = len(x_axis)
        plt.plot(x_axis, y_axis, color=colors[alg_c], label=alg_name_1)
        alg_c += 1
    plt.legend(framealpha=1, frameon=True)
    plt.title('%s' % log_name)
    plt.ylabel('Pareto Progress')
    plt.xlabel(x_names[name_index])
    plt.savefig("%s%s.pdf" % (file_path, name_files[name_index]))
    plt.show()
    return func_eval


def plot_pareto_front(file_path, algorithm_results, joint_pareto_info):
    colors = ['r', 'b', 'g']
    for alg_name in algorithm_results:
        [log_name, alg_name_1] = extract_log_alg_name(alg_name)
        pareto_front = algorithm_results[alg_name].pareto_front
        color_taken = [False, False, False]
        for s_id in joint_pareto_info:
            s_info = joint_pareto_info[s_id]
            if s_id not in pareto_front:
                if color_taken[1]:
                    plt.plot(s_info.cycle_time(), s_info.execution_cost(), color='b', marker='o')
                else:
                    plt.plot(s_info.cycle_time(), s_info.execution_cost(), color='b', marker='o', label='JP - P')
                color_taken[1] = True
        for s_id in pareto_front:
            s_info = pareto_front[s_id]
            i_color = 0 if s_id not in joint_pareto_info else 2
            l_name = 'P - JP' if s_id not in joint_pareto_info else 'P & JP'
            if color_taken[i_color]:
                plt.plot(s_info.cycle_time(), s_info.execution_cost(), color=colors[i_color], marker='o')
            else:
                plt.plot(s_info.cycle_time(), s_info.execution_cost(), color=colors[i_color], marker='o', label=l_name)
            color_taken[i_color] = True
        plt.ticklabel_format(axis="x", style="sci", scilimits=(0, 0))
        plt.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        plt.legend(framealpha=1, frameon=True)
        plt.title('%s(%s)' % (alg_name_1, log_name))
        plt.ylabel('Resource Allocation Cost')
        plt.xlabel('Cycle Time')
        plt.savefig("%splot_pareto_front_%s.pdf" % (file_path, alg_name_1))
        plt.show()


def extract_log_alg_name(full_alg_name:str):
    name_list = full_alg_name.split("_")
    log_name = name_list[0]
    algs = ['hill', 'tabu', 'nsga2', 'with', 'without']
    approaches = ['combined', 'only', 'calendar', 'add', 'first']
    for i in range(1, len(name_list)):
        if name_list[i] in algs:
            break
        log_name += '_' + name_list[i]
    for i in range(1, len(name_list)):
        if name_list[i] in approaches:
            break
        log_name += '_' + name_list[i]
    alg_name = ''
    if 'hill' in name_list:
        alg_name = 'HC_'
    if 'tabu' in name_list:
        alg_name = 'TS_'
    if 'nsga2' in name_list:
        alg_name = 'NSGA-II'
    if 'with' in name_list:
        alg_name += 'FLEX'
    if 'without' in name_list:
        alg_name += 'STRICT'
    if 'combined' in name_list:
        alg_name += '_CO'
    if 'first' in name_list:
        alg_name += '_F'
        next_idx = name_list.index('first') + 1
        if name_list[next_idx] == 'calendar':
            alg_name += '_CA_T_A_R'
        else:
            alg_name += '_A_R_T_CA'
    if 'only' in name_list:
        alg_name += '_O'
        if 'calendar' in name_list:
            alg_name += '_C'
        if 'add' in name_list:
            alg_name += '_A_R'
    return [log_name, alg_name]


def fill_str(in_str, m_lenght):
    return in_str + (' ' * (m_lenght - len(in_str)))


def save_allocation_statistics_into_SolutionObject(alg_name:str, algorithm_result:AlgorithmResults, funct_eval: int, general_info: tuple[float, float, float], metrics: tuple[float, float, float, float], impr_index: tuple[float, float]):

    out = SolutionOutputObject()
    out.name = alg_name
    out.time_metric = impr_index[0]
    out.cost_metric = impr_index[1]

    out.func_ev = funct_eval
    out.total_explored = 0  # TODO Which value?
    out.pareto_size = len(algorithm_result.pareto_front)
    out.in_jp = general_info[0]
    out.ave_time = general_info[1]
    out.ave_cost = general_info[2]

    out.hyperarea = metrics[0]
    out.hausd_dist = metrics[1]
    out.delta_sprd = metrics[2]
    out.purity_rate = metrics[3]

    out.pareto_values = []
    for v in algorithm_result.pareto_front:
        new_obj = SolutionOutputParetoValue(name=v, sim_params=algorithm_result.pareto_front[v].sim_params, # type: ignore
                       cons_params=algorithm_result.pareto_front[v].cons_params, # type: ignore
                       median_cycle_time=algorithm_result.pareto_front[v].median_cycle_time,
                       median_execution_cost=algorithm_result.pareto_front[v].median_execution_cost,)
        out.pareto_values.append(new_obj)

    return out


def save_allocation_statistics(file_path, algorithm_result, funct_eval, general_info, metrics):
    print(file_path)
    f_writer = open(file_path, "w")
    f_writer.write("Function Evaluations:  %d\n" % funct_eval)
    f_writer.write("Solutions Explored:    %d\n" % len(algorithm_result.explored_solutions))
    f_writer.write("Pareto front size:     %d\n" % len(algorithm_result.pareto_front))
    f_writer.write("In Joint Pareto:       %d\n" % general_info[0])
    f_writer.write("Not In Joint Pareto:   %d\n" % (len(algorithm_result.pareto_front) - general_info[0]))
    f_writer.write("Average Cycle Time:    %s\n" % str(str(datetime.timedelta(seconds=general_info[1]))))
    f_writer.write("Average Resource Cost: %f\n" % general_info[2])
    f_writer.write('------------------------- METRICS --------------------------\n')
    f_writer.write("# Hyperarea Ratio:     %f\n" % metrics[0])
    f_writer.write("# Hausdorff Distance:  %f\n" % metrics[1])
    f_writer.write("# Delta Metric:        %f\n" % metrics[2])
    f_writer.write("# Purity Metric:       %f\n" % metrics[3])
    f_writer.write('--------------- OPTIMAL RESOURCE ALLOCATIONS ----------------\n')
    max_len = 0
    for sol_id in algorithm_result.pareto_front:
        max_len = max(max_len, len("%.2f" % round(algorithm_result.pareto_front[sol_id].execution_cost(), 2)))
    for sol_id in algorithm_result.pareto_front:
        print_allocation_info(f_writer, algorithm_result, sol_id, max_len)


def print_allocation_info(f_writer, algorithm_result, sol_id, max_len):
    to_print = '['
    is_first = True
    to_print += str(sol_id)
    # for resource_info in algorithm_result.resource_pools[sol_id]:
    #     if not is_first:
    #         to_print += ', '
    #     to_print += ("%s:" % resource_info.resource_name)
    #     to_print += ("  " if resource_info.resource_count < 10 else " ") + ("%d" % resource_info.resource_count)
    #     is_first = False
    a_cost = ("%.2f" % round(algorithm_result.pareto_front[sol_id].execution_cost(), 2))
    space = ' ' * (max_len - len(a_cost))
    to_print += ('] -> [aCost: %s, cTime: %s]\n'
                 % (space + a_cost,
                    str(str(datetime.timedelta(seconds=algorithm_result.pareto_front[sol_id].cycle_time())))))
    f_writer.write(to_print)


