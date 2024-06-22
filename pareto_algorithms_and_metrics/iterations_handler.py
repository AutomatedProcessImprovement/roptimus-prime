import copy
from typing import Dict, Optional

from data_structures.RosterManager import RosterManager
from data_structures.iteration_info import IterationInfo, IterationNextType
from data_structures.pools_info import PoolInfo
from data_structures.priority_queue import PriorityQueue
from data_structures.simulation_info import SimulationInfo
from support_modules.prosimos_simulation_runner import perform_simulations
from pareto_algorithms_and_metrics.pareto_metrics import try_update_pareto_front, min_dist_from_pareto
from support_modules.json_manager import JsonManager


def _in_non_optimal_distance_thresold(distance):
    return distance < 1000


class IterationHandler:
    def __init__(self, log_name, pools_info:PoolInfo, is_tabu_search, with_mad, resource_manager):

        self.log_name = log_name
        self.is_tabu_search = is_tabu_search
        self.with_mad = with_mad

        self.resource_manager: RosterManager = resource_manager
        self.time_table_path = self.resource_manager.write_to_file()

        simulation = perform_simulations(pools_info, log_name, 0,
                                         self.time_table_path)
        simulation_info:SimulationInfo = simulation[0]
        self.traces = simulation[1]

        self.generated_solutions:Dict[str,IterationInfo] = {pools_info.id: IterationInfo(pools_info, simulation_info, 0)}
        self.solution_order = [pools_info.id]
        self.pareto_front = {pools_info.id: simulation_info}

        self.real_pareto_front = {pools_info.id: simulation_info}
        self.pareto_update_distance = 0

        self.print_iteration_info(True, pools_info, 0)

        self.discarded_queue = PriorityQueue()
        self.execution_queue = PriorityQueue()
        self.execution_queue.add_task(pools_info.id,
                                      self._solution_quality(simulation_info))

        self.jsonManager = JsonManager()
        self.jsonManager.write_accepted_solution_timetable_to_json_files(
            self.time_table_path, self.resource_manager.constraints_path, pools_info.id)
        self.current_starting_id = pools_info.id


    def update_priorities(self):
        for in_discarded in [True, False]:
            new_queue = PriorityQueue()
            old_queue = self.discarded_queue if in_discarded else self.execution_queue
            while not old_queue.is_empty():
                sol_id = old_queue.pop_task()    
                simulation_info = self.generated_solutions[sol_id].simulation_info # type: ignore
                new_queue.add_task(self.generated_solutions[sol_id].pools_info.id, # type: ignore
                                   self._solution_quality(simulation_info))
            if in_discarded:
                self.discarded_queue = new_queue
            else:
                self.execution_queue = new_queue

    def pop_next_solution(self):
        if not self.is_tabu_search:
            return self.execution_queue.pop_task()
        if self.execution_queue.is_empty():
            return self.discarded_queue.pop_task()
        return self.execution_queue.pop_task()

    def has_next(self):
        if not self.is_tabu_search:
            return not self.execution_queue.is_empty()
        return (not self.execution_queue.is_empty()) or (not self.discarded_queue.is_empty())

    def pq_size_print(self):
        return len(self.execution_queue.pq)

    def next(self) -> IterationNextType:
        to_return = self._move_next()
        if self.is_tabu_search and to_return[0] is None:
            current_solution = self.discarded_queue.pop_task()
            return (None, None, -1) if current_solution is None \
                else (self.generated_solutions[current_solution].pools_info,
                      self.generated_solutions[current_solution].simulation_info,
                      self.generated_solutions[current_solution].non_optimal_distance)
        return to_return

    def getCurrentIterationInfo(self):
        return self.generated_solutions[self.current_starting_id]

    def clean_up_json(self):
        self.jsonManager.retrieve_json_from_id(self.current_starting_id,
                                               self.resource_manager.time_table_path,
                                               self.resource_manager.constraints_path)
        self.resource_manager = RosterManager(self.log_name,
                                              self.resource_manager.time_table_path,
                                              self.resource_manager.constraints_path)


    def _move_next(self) -> IterationNextType:
        if not self.execution_queue.is_empty():
            current_solution = self.execution_queue.pop_task()

            while current_solution is not None:
                # self.generated_solutions
                pools_info = self.generated_solutions[current_solution].pools_info
                simulation_info = self.generated_solutions[current_solution].simulation_info
                if pools_info.id in self.pareto_front:
                    self.jsonManager.retrieve_json_from_id(current_solution, self.resource_manager.time_table_path,
                                                          self.resource_manager.constraints_path)
                    self.resource_manager = RosterManager(self.log_name, self.resource_manager.time_table_path,
                                                          self.resource_manager.constraints_path)
                    # self.resource_manager.time_table = "./json_files/"+str(current_solution)+"/timetable.json"
                    # self.resource_manager.constraints_json = "./json_files/"+str(current_solution)+"/constraints.json"
                    self.current_starting_id = current_solution
                    return (pools_info,
                            simulation_info,
                            self.generated_solutions[current_solution].non_optimal_distance)
                elif self.is_tabu_search:
                    self.discarded_queue.add_task(pools_info.id, self._solution_quality(simulation_info))
                current_solution = self.execution_queue.pop_task()
        return (None, None, -1)

    def solutions_count(self):
        return len(self.generated_solutions)

    def is_solution_tried(self, sol_id):
        return sol_id in self.generated_solutions

    def try_new_solution(self, pools_info, distance):
        # self.resource_manager.update_roster(pools_info)
        if pools_info.id not in self.generated_solutions:
            # update_resource_pools(pools_info.pools, pools_info.task_pools)  # Updating Simulation Model with new pool allocation
            # Update simulation info with new pools info
            # raise Exception("CRASH ON PURPOSE")
            (simulation_info, traces) = perform_simulations(pools_info,
                                                            self.log_name,
                                                            len(self.generated_solutions),
                                                            json_path=self.time_table_path)  # Running/retrieving simulation results
            self.traces = traces
            if simulation_info is None:
                self.clean_up_json()
                return False
            is_valid = self.check_optimals_hill_climbing(pools_info,
                                                         simulation_info,
                                                         distance)  # Verifying optimality of solution
            self.print_iteration_info(is_valid, pools_info, distance)

            if (not is_valid) and self.is_tabu_search:
                self.check_optimals_tabu_search(pools_info, simulation_info)
            # Regardless of if it's a valid pareto or not, reset the jsons
            self.clean_up_json()
            return is_valid
        self.clean_up_json()
        return False

    def check_last_pareto_update_distance(self, pools_info, simulation_info, is_valid):
        is_updated = False
        if self.with_mad:
            [is_updated, self.real_pareto_front] = try_update_pareto_front(pools_info.id, simulation_info,
                                                                           self.real_pareto_front, False)
            self.pareto_update_distance = 0 if is_updated else self.pareto_update_distance + 1
        else:
            self.pareto_update_distance = 0 if is_valid else self.pareto_update_distance + 1
        return is_valid or is_updated

    def _solution_quality(self, simulation_info):
        pareto_front = self.real_pareto_front if self.with_mad else self.pareto_front
        if simulation_info.pools_info.id in pareto_front:
            return -1 * len(self.generated_solutions)
        return min_dist_from_pareto(pareto_front, simulation_info)
        # return doa_pareto_to_point(pareto_front, simulation_info)

    def check_optimals_hill_climbing(self, pools_info, simulation_info, distance):
        """
        Hill-Climbing only considers solutions noot dominated by the current one
        Sub-optimal candidates. i.e., those improving only one (or 0) dimention are discarded
        """

        # Each solution candidate is counted just once
        self.generated_solutions[pools_info.id] = IterationInfo(pools_info, simulation_info,
                                                                len(self.generated_solutions), distance)
        self.solution_order.append(pools_info.id)

        [is_optimal_candidate, self.pareto_front] = try_update_pareto_front(pools_info.id, simulation_info,
                                                                            self.pareto_front, self.with_mad)
        if is_optimal_candidate:
            self.update_priorities()

        is_optimal_candidate = self.check_last_pareto_update_distance(pools_info, simulation_info, is_optimal_candidate)

        # We always write the solution down, so we have it for later reference, e.g. b frontend
        self.jsonManager.write_accepted_solution_timetable_to_json_files(self.resource_manager.time_table_path,
                                                                            self.resource_manager.constraints_path,
                                                                            pools_info.id)

        if is_optimal_candidate:
            # IF: New solution is not dominated by the previous current solution
            # AND the dimention that isn't improving does not deviate too much from initial solution
            self.execution_queue.add_task(pools_info.id, self._solution_quality(simulation_info))
            
            return True
        return False

    def check_optimals_tabu_search(self, pools_info, simulation_info):
        """
        Extends Hill-Climbing to also consider sub-optimal solutions
        Sub-optimal candidates, improves at least on dimention of the initial solution ()
        """

        if _in_non_optimal_distance_thresold(self.generated_solutions[pools_info.id].non_optimal_distance):
            # Adding sub-optimal solution to the queue to be used as input for future iterations

            self.generated_solutions[pools_info.id].non_optimal_distance += 1

            self.discarded_queue.add_task(pools_info.id, self._solution_quality(simulation_info))
            return True
        return False

    def print_iteration_info(self, is_valid_solution, pools_info, distance):
        if is_valid_solution:
            print("ADDED: " + pools_info.id)
        elif self.is_tabu_search and _in_non_optimal_distance_thresold(distance):
            print("NO-DISCARDED(%d): %s" % (distance, pools_info.id))
        else:
            print("DISCARDED: " + pools_info.id)

        if self.with_mad:
            print("Pareto Size:  %d (%d) / %d" % (len(self.pareto_front), len(self.real_pareto_front),
                                                  len(self.generated_solutions)))
        else:
            print("Pareto Size:  %d / %d" % (len(self.pareto_front), len(self.generated_solutions)))
        print("Last accepted:  %d" % self.pareto_update_distance)

        print("------------------------------------------------------------------------------------")
