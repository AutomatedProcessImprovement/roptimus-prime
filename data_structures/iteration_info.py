import copy
from typing import Optional

from data_structures.pools_info import PoolInfo
from data_structures.simulation_info import SimulationInfo


IterationNextType = tuple[Optional[PoolInfo], Optional[SimulationInfo], int]

class IterationInfo:
    def __init__(self, pools_info: PoolInfo, simulation_info: SimulationInfo, it_number: int, non_optimal_distance=0):
        self.it_number = it_number
        self.pools_info = copy.deepcopy(pools_info)
        self.simulation_info = copy.deepcopy(simulation_info)
        self.non_optimal_distance= non_optimal_distance

