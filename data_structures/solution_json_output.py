from typing import Optional, TypedDict
from data_structures.constraints import ConstraintsType
from data_structures.simulation_info import SimulationInfo
from data_structures.solution_space import SolutionOutputObject, SolutionOutputParetoValue
from data_structures.timetable import TimetableType

class Solution(TypedDict):
    info: SimulationInfo
    sim_params: TimetableType
    cons_params:ConstraintsType

class FullOutputJson(TypedDict):
    name: str
    initial_simulation_info: Optional[Solution]
    final_solutions: Optional[list[SolutionOutputObject]]
    current_solution_info: Optional[Solution]
    