import json
from typing import Optional, TypedDict

from data_structures.constraints import ConstraintsType
from data_structures.timetable import  TimetableType


class SolutionSpace:
    def __init__(self, it_number=0, execution_cost=0.0, cycle_time=0.0, time_deviation=0.0, cost_deviation=0.0,
                 simulation_duration=0.0):
        self.it_number = it_number
        self.median_execution_cost = execution_cost
        self.median_cycle_time = cycle_time
        self._simulation_duration = simulation_duration
        self.deviation_info = DeviationInfo(time_deviation, cost_deviation)
        self.sim_params: Optional[TimetableType] = None
        self.cons_params: Optional[ConstraintsType] = None

    def cycle_time(self):
        return self.median_cycle_time

    def simulation_duration(self):
        return self._simulation_duration

    def execution_cost(self):
        return self.median_execution_cost
    
    def to_json(self):
        return {
            "it_number": self.it_number,
            "median_execution_cost": self.median_execution_cost,
            "median_cycle_time": self.median_cycle_time,
            "simulation_duration": self._simulation_duration,
            "deviation_info": self.deviation_info.to_json(),
        }


class ResourceInfo:
    def __init__(self, resource_name:str, resource_count:float, resource_utilization:float, cost_per_unit:float):
        self.resource_name = resource_name
        self.resource_count = resource_count
        self.resource_utilization = resource_utilization
        self.cost_per_unit = cost_per_unit
    
    def to_json(self):
        return self.__dict__


class DeviationInfo:
    def __init__(self, cycle_time_deviation, execution_duration_deviation, dev_type=0):
        self.p_cycle_time_deviation = cycle_time_deviation
        self.p_execution_duration_deviation = execution_duration_deviation
        self.dev_type = dev_type

    def cycle_time_deviation(self):
        return self.p_cycle_time_deviation if self.dev_type == 0 else self._calculated_deviation()

    def execution_duration_deviation(self):
        return self.p_execution_duration_deviation if self.dev_type == 0 else self._calculated_deviation()

    def _calculated_deviation(self):
        if self.dev_type == 1:
            return min(self.p_execution_duration_deviation, self.p_cycle_time_deviation)
        return max(self.p_execution_duration_deviation, self.p_cycle_time_deviation)
    
    def to_json(self):
        return {
            "cycle_time_deviation": self.p_cycle_time_deviation,
            "execution_duration_deviation": self.p_execution_duration_deviation,
            "dev_type": self.dev_type
        }


class SolutionOutputObject:
    def __init__(self):
        self.name = ""
        self.func_ev :float = 0
        self.total_explored :float = 0
        self.pareto_size :float = 0
        self.in_jp :float = 0
        self.not_in_jp :float = 0
        self.hyperarea :float = 0
        self.hausd_dist :float = 0
        self.delta_sprd :float = 0
        self.purity_rate :float = 0
        self.ave_time :float = 0
        self.ave_cost :float = 0
        self.time_metric :float = 0
        self.cost_metric :float = 0
        

    def to_json(self):
        return self.__dict__
    
    

