from typing import Optional, TypedDict
from data_structures.constraints import ConstraintsType
from data_structures.iteration_info import IterationInfo
from data_structures.simulation_info import SimulationInfo
from data_structures.solution_space import ResourceInfo, SolutionOutputObject, SolutionSpace
from data_structures.timetable import TimetableType
from support_modules.file_manager import load_constraints_for_key, load_timetable_for_key

class SolutionJson(TypedDict):
    solution_info: SimulationInfo
    sim_params: TimetableType
    cons_params: ConstraintsType
    name: str


class FullOutputJson(TypedDict):
    name: str
    initial_solution: Optional[SolutionJson]
    final_solutions: Optional[list[SolutionJson]]
    final_solution_metrics: Optional[list[SolutionOutputObject]]
    current_solution: Optional[SolutionJson]
    

def iteration_info_to_solution(iteration_entry: tuple[str, IterationInfo]) -> Optional[SolutionJson]:
        approach, iteration = iteration_entry
        key = iteration.pools_info.id
        sim_params = load_timetable_for_key(key)
        cons_params = load_constraints_for_key(key)
        if sim_params is None or cons_params is None:
            return None
        return SolutionJson(
            solution_info=iteration.simulation_info,
            sim_params=sim_params,
            cons_params=cons_params,
            name=f"{approach} #{iteration.it_number}"
        )