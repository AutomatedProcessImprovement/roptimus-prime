from typing import Optional, TypedDict
from data_structures.constraints import ConstraintsType
from data_structures.simulation_info import SimulationInfo
from data_structures.solution_space import ResourceInfo, SolutionOutputObject, SolutionSpace
from data_structures.timetable import TimetableType

class SolutionJson(TypedDict):
    solution_info: SimulationInfo
    sim_params: TimetableType
    cons_params: ConstraintsType


class FullOutputJson(TypedDict):
    name: str
    initial_solution: Optional[SolutionJson]
    final_solutions: Optional[list[SolutionJson]]
    final_solution_metrics: Optional[list[SolutionOutputObject]]
    current_solution: Optional[SolutionJson]
    