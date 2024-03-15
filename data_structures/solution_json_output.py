from typing import Optional, TypedDict
from data_structures.constraints import ConstraintsType
from data_structures.iteration_info import IterationInfo
from data_structures.simulation_info import SimulationInfo
from data_structures.solution_space import ResourceInfo, SolutionOutputObject, SolutionSpace
from data_structures.timetable import TimetableType
from support_modules.file_manager import StatsType



class FullOutputJson(TypedDict):
    name: str
    initial_simulation_info: Optional[SimulationInfo]
    final_solutions: Optional[list[SimulationInfo]]
    final_solution_metrics: Optional[list[SolutionOutputObject]]
    current_solution_info: Optional[SimulationInfo]
    