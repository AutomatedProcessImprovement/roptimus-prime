import json
import os
import sys
import math
import tempfile

from support_modules.file_manager import read_stats_file

curr_dir_path = os.path.abspath(os.path.dirname(__file__))


class ExtremeValues:
    def __init__(self):
        self.min_cost = sys.float_info.max
        self.min_time = sys.float_info.max
        self.max_cost = 0
        self.max_time = 0
        self.best_cost_point = [sys.float_info.max, sys.float_info.max]
        self.best_time_point = [sys.float_info.max, sys.float_info.max]
        self.worst_cost_point = [0, 0]
        self.worst_time_point = [0, 0]

    # From all the discovered paretos
    def update_good_bad_points(self, sol_info):
        s_cost = sol_info.execution_cost()
        s_time = sol_info.cycle_time()
        self.min_cost = min(self.min_cost, s_cost)
        self.min_time = min(self.min_time, s_time)
        self.max_cost = max(self.max_cost, s_cost)
        self.max_time = max(self.max_time, s_time)

    # From joint-pareto
    def update_pareto_extremes(self, sol_info):
        s_cost = sol_info.execution_cost()
        s_time = sol_info.cycle_time()
        if is_lower_than(s_cost, self.best_cost_point[0], s_time, self.best_cost_point[1]):
            self.best_cost_point = [s_cost, s_time]
        if is_lower_than(s_time, self.best_time_point[1], s_cost, self.best_time_point[0]):
            self.best_time_point = [s_cost, s_time]
        if is_greater_than(s_cost, self.worst_cost_point[0], s_time, self.worst_cost_point[1]):
            self.worst_cost_point = [s_cost, s_time]
        if is_greater_than(s_time, self.worst_time_point[1], s_cost, self.worst_time_point[0]):
            self.worst_time_point = [s_cost, s_time]

class AlgorithmResults:
    def __init__(self, execution_info, with_mad):
        self.explored_solutions = execution_info[0]
        self.resource_pools = execution_info[1]
        [self.pareto_front, self.initial_solution] = find_pareto_front([self.explored_solutions], with_mad)

        for key in self.pareto_front:
            print(key)

            with open(os.path.abspath(os.path.join(tempfile.gettempdir(), 'roptimos/',  'json_files/'+str(key)+"/constraints.json")), 'r') as c_read:
                cons = json.load(c_read)
            with open(os.path.abspath(os.path.join(tempfile.gettempdir(), 'roptimos/',  'json_files/'+str(key)+"/timetable.json")), 'r') as t_read:
                ttb = json.load(t_read)

            self.pareto_front[key].sim_params = ttb
            self.pareto_front[key].cons_params = cons



class GlobalParetoMetrics:
    def __init__(self, log_name, algorithm_names):
        self.initial_solution = ''
        self.algorithm_results = dict()
        self.joint_extreme_values = ExtremeValues()
        for alg_name in algorithm_names:
            execution_info = read_stats_file(log_name, alg_name)
            if execution_info is None:
                continue
            without_mad_alg_result = AlgorithmResults(execution_info, False)
            self.algorithm_results["%s_%s" % (log_name, alg_name)] = without_mad_alg_result
            self.initial_solution = without_mad_alg_result.initial_solution

        [self.joint_pareto_info, self.total_explored_solution] = find_joint_pareto(self.algorithm_results,
                                                                                   self.joint_extreme_values)
        self.joint_pareto_hyperarea = hyperarea_metric(self.joint_pareto_info, self.joint_extreme_values)

    def compute_metrics(self, pareto_front):
        gamma_delta = gamma_delta_metric(pareto_front, self.joint_extreme_values)
        hyperarea_diff = hyperarea_ratio(pareto_front, self.joint_extreme_values, self.joint_pareto_hyperarea)
        hausdorff_dist = averaged_hausdorff_distance(pareto_front, self.joint_pareto_info)
        purity = purity_metric(pareto_front, self.joint_pareto_info)
        return [hyperarea_diff, hausdorff_dist, gamma_delta[1], purity]


# ------------- Pareto Front Operations --------------------- #
# ----------------------------------------------------------- #

def find_pareto_front(explored_solutions_list, with_mad):
    pareto_front = dict()
    f_pareto_front = dict()
    initial_solution = ''
    for explored_solutions in explored_solutions_list:
        for sol_id in explored_solutions:
            if explored_solutions[sol_id].it_number == 0:
                f_pareto_front[sol_id] = explored_solutions[sol_id]
                initial_solution = sol_id
            in_pareto = True
            for to_compare in explored_solutions_list:
                if sol_id in pareto_front or not in_pareto_front(explored_solutions[sol_id], to_compare, with_mad):
                    in_pareto = False
                    break
            if in_pareto:
                pareto_front[sol_id] = explored_solutions[sol_id]
            f_pareto_front = try_update_pareto_front(sol_id, explored_solutions[sol_id], f_pareto_front, with_mad)[1]

    return [pareto_front, initial_solution]


def find_joint_pareto(algorithm_results, joint_extreme_values):
    joint_pareto = dict()
    full_solutions = set()
    temp_pareto = dict()
    for alg_name in algorithm_results:
        explored_solutions = algorithm_results[alg_name].explored_solutions
        update_good_bad_points(joint_extreme_values, explored_solutions)
        for sol_id in explored_solutions:
            full_solutions.add(sol_id)
            if sol_id not in temp_pareto:
                temp_pareto[sol_id] = explored_solutions[sol_id]
    for sol_cand in temp_pareto:
        add_pareto = True
        for to_compare in temp_pareto:
            if is_dominated_by(temp_pareto[sol_cand], temp_pareto[to_compare], False):
                add_pareto = False
                break
        if add_pareto:
            joint_pareto[sol_cand] = temp_pareto[sol_cand]
    update_extreme_values(joint_extreme_values, joint_pareto)
    return [joint_pareto, len(full_solutions)]


def try_update_pareto_front(new_sol_id, new_solution, pareto_front, with_mad):
    if not in_pareto_front(new_solution, pareto_front, with_mad):
        return [False, pareto_front]
    new_pareto = {new_sol_id: new_solution}

    for sol_id in pareto_front:
        if not is_dominated_by(pareto_front[sol_id], new_solution, with_mad):
            new_pareto[sol_id] = pareto_front[sol_id]
    return [True, new_pareto]


def in_pareto_front(candidate_info, explored_solutions, with_mad):
    for sol_id in explored_solutions:
        if is_dominated_by(candidate_info, explored_solutions[sol_id], with_mad):
            return False
    return True


def update_extreme_values(extreme_values, pareto_front):
    for sol_id in pareto_front:
        extreme_values.update_pareto_extremes(pareto_front[sol_id])


def update_good_bad_points(extreme_values, pareto_front):
    for sol_id in pareto_front:
        extreme_values.update_good_bad_points(pareto_front[sol_id])


def is_dominated_by(dominated_info, dominant_info, with_mad):
    is_not_mad_dominated = is_non_mad_dominated(dominated_info, dominant_info)
    return is_not_mad_dominated and is_mad_dominated(dominated_info, dominant_info) if with_mad \
        else is_not_mad_dominated


def is_non_mad_dominated(dominated_info, dominant_info):
    return dominant_info.cycle_time() < dominated_info.cycle_time() \
           and dominant_info.execution_cost() < dominated_info.execution_cost()


def is_mad_dominated(dominated_info, dominant_info):
    dev_dominated = dominated_info.deviation_info
    dev_dominant = dominant_info.deviation_info
    return \
        abs(dominated_info.cycle_time() - dominant_info.cycle_time()) \
        > min(dev_dominant.cycle_time_deviation(), dev_dominated.cycle_time_deviation()) \
        and \
        abs(dominated_info.simulation_duration() - dominant_info.simulation_duration()) \
        > min(dev_dominant.execution_duration_deviation(), dev_dominated.execution_duration_deviation())


# ------------- Metrics to Assess Pareto Fronts ---------------- #
# -------------------------------------------------------------- #

def purity_metric(pareto_front, global_pareto):
    in_global_pareto = 0
    for alg_sol in pareto_front:
        if alg_sol in global_pareto:
            in_global_pareto += 1
    return in_global_pareto / len(pareto_front)


def gamma_delta_metric(pareto_front, joint_extreme_values):
    sorted_values = [sorted(pareto_front, key=lambda x: pareto_front[x].execution_cost()),
                     sorted(pareto_front, key=lambda x: pareto_front[x].cycle_time())]
    gamma_metric = 0
    delta_metric = 0
    index = 0
    for sorted_array in sorted_values:
        [p_cost, p_time] = find_cost_time(pareto_front, sorted_array[0])
        [d_0, d_n] = find_extreme_point_distance(joint_extreme_values,
                                                 find_cost_time(pareto_front, sorted_array[0]),
                                                 find_cost_time(pareto_front, sorted_array[len(sorted_array) - 1]),
                                                 index)
        gamma_metric = max(gamma_metric, d_0, d_n)
        total_distance_sum = 0
        distances = []
        for i in range(1, len(sorted_array)):
            [c_cost, c_time] = find_cost_time(pareto_front, sorted_array[i])
            distances.append(eucl_distance(p_cost, p_time, c_cost, c_time))
            total_distance_sum += distances[i - 1]
            gamma_metric = max(gamma_metric, distances[i - 1])
            p_cost = c_cost
            p_time = c_time
        mean_distance = 0 if len(sorted_array) == 1 else total_distance_sum / (len(sorted_array) - 1)
        mean_diff_sum = 0
        for i in range(0, len(distances)):
            mean_diff_sum += abs(distances[i] - mean_distance)
        delta_metric = (d_0 + d_n + mean_diff_sum) / (d_0 + d_n + (len(distances) * mean_distance))
        index += 1
    return [gamma_metric, delta_metric]


def hyperarea_metric(pareto_front, global_extreme_values):
    sorted_optimals = sorted(pareto_front, key=lambda x: pareto_front[x].cycle_time())
    inferior_area = 0
    c_cost = global_extreme_values.max_cost
    c_time = global_extreme_values.max_time
    for i in range(len(sorted_optimals)):
        sol_info = pareto_front[sorted_optimals[i]]
        cost, time = sol_info.execution_cost(), sol_info.cycle_time()
        if c_cost > cost:
            inferior_area += ((c_cost - cost) * (c_time - time))
            c_cost = cost
    return inferior_area


def hyperarea_ratio(pareto_front, global_extreme_values, joint_pareto_hyperarea):
    pareto_hyperarea = hyperarea_metric(pareto_front, global_extreme_values)
    return pareto_hyperarea / joint_pareto_hyperarea


def averaged_hausdorff_distance(pareto_front, joint_pareto):
    return max(compute_d_xy_norm_2(pareto_front, joint_pareto), compute_d_xy_norm_2(joint_pareto, pareto_front))


def compute_d_xy_norm_2(vector_1, vector_2):
    cumulative_sum = 0
    for sol_id in vector_1:
        [c_1, t_1] = find_cost_time(vector_1, sol_id)
        min_distance = sys.float_info.max
        for joint_id in vector_2:
            [c_2, t_2] = find_cost_time(vector_2, joint_id)
            min_distance = min(min_distance, eucl_distance(c_1, t_1, c_2, t_2))
        cumulative_sum += pow(min_distance, 2)
    return math.sqrt(cumulative_sum) / math.sqrt(len(vector_1))


def min_dist_from_pareto(pareto_front, point_info):
    distance = sys.float_info.max
    for sol_id in pareto_front:
        [p_cost, p_time] = find_cost_time(pareto_front, sol_id)
        distance = min(distance, eucl_distance(point_info.execution_cost(), point_info.cycle_time(), p_cost, p_time))
    return distance


def find_extreme_point_distance(extreme_values, point_0, point_n, dimention_index):
    p_0 = extreme_values.best_cost_point if dimention_index == 0 else extreme_values.best_time_point
    p_n = extreme_values.worst_cost_point if dimention_index == 0 else extreme_values.worst_time_point
    d_0 = eucl_distance(p_0[0], p_0[1], point_0[0], point_0[1])
    d_n = eucl_distance(point_n[0], point_n[1], p_n[0], p_n[1])
    return [d_0, d_n]


def find_cost_time(generated_solutions, sol_id):
    return [generated_solutions[sol_id].execution_cost(),
            generated_solutions[sol_id].cycle_time()]


def eucl_distance(cost_1, time_1, cost_2, time_2):
    return math.sqrt(pow(cost_2 - cost_1, 2) + pow(time_2 - time_1, 2))


def eucl_distance_0(cost_1, time_1, cost_2, time_2):
    return math.sqrt(pow(max(0, cost_1 - cost_2), 2) + pow(max(0, time_1 - time_2), 2))


def is_lower_than(x_1, x_2, y_1, y_2):
    return x_1 < x_2 or (x_1 == x_2 and y_1 < y_2)


def is_greater_than(x_1, x_2, y_1, y_2):
    return x_1 > x_2 or (x_1 == x_2 and y_1 > y_2)
