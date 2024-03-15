from typing import Optional, TypedDict
from data_structures.constraints import ConstraintsType
from data_structures.simulation_info import SimulationInfo
from data_structures.solution_space import ResourceInfo, SolutionOutputObject, SolutionOutputParetoValue, SolutionSpace
from data_structures.timetable import TimetableType
from support_modules.file_manager import StatsType

class SolutionJson(TypedDict):
    solution_space: SolutionSpace
    resources_info: dict[str,ResourceInfo]
    sim_params: TimetableType
    cons_params:ConstraintsType

class FullOutputJson(TypedDict):
    name: str
    initial_simulation_info: Optional[SolutionJson]
    final_solutions: Optional[list[SolutionJson]]
    final_solution_metrics: Optional[list[SolutionOutputObject]]
    current_solution_info: Optional[SolutionJson]
    