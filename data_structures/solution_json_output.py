from typing import Optional
from data_structures.simulation_info import SimulationInfo
from data_structures.solution_space import SolutionOutputParetoValue


class SolutionJSONOutput(SolutionOutputParetoValue):
    initial_simulation_info: Optional[SimulationInfo]
    current_simulation_info: SimulationInfo
