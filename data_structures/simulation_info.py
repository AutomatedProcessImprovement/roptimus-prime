from datetime import datetime
from typing import Dict, Optional
from data_structures.pools_info import PoolInfo
from data_structures.solution_space import DeviationInfo


class SimulationInfo:
    def __init__(self, pools_info: PoolInfo):
        self.pools_info: PoolInfo = pools_info
        self.mean_process_cycle_time: float = 0
        self.simulation_start_date:Optional[datetime] = None
        self.simulation_end_date:Optional[datetime] = None
        self.simulation_time: float = 0

        self.deviation_info = DeviationInfo(0.0, 0.0)

        self.pool_utilization: Dict[str,float] = dict()

        self.pool_time: Dict[str,float] = dict()

        self.pool_cost:Dict[str,float] = dict()
        self.total_pool_cost: float = 0
        self.total_pool_time: float = 0

        self.available_time: Dict[str, float] = dict()

    # TODO -> Add resources that did not participate in the process, put pool_time = 0 and pool_cost = duration * cost_hour
    def init_pool_time_cost(self):
        return

    def cycle_time(self):
        return self.mean_process_cycle_time

    def execution_cost(self):
        return self.pools_info.pools_total_cost * self.simulation_duration() / 3600

    def simulation_duration(self):
        if self.simulation_start_date is not None and self.simulation_end_date is not None:
            return (self.simulation_end_date - self.simulation_start_date).total_seconds()
        else:
            return 0

    def pool_time_outturn(self, pool_name):
        return self.pool_time[pool_name] / self.total_pool_time

    def pool_cost_outturn(self, pool_name):
        return self.pool_cost[pool_name] / self.total_pool_cost

    def pool_outturn(self, pool_name):
        if pool_name in self.pool_cost:
            return self.pool_cost_outturn(pool_name) + self.pool_time_outturn(pool_name)
        return 0

    def update_pools_info(self, pools_info):
        self.pools_info = pools_info

    def update_simulation_period(self, start_date, end_date):
        self.simulation_start_date = start_date
        self.simulation_end_date = end_date

    def update_resource_utilization(self, pool_name, utilization_ratio):
        self.pool_utilization[pool_name] = utilization_ratio

    def update_resource_available_time(self, pool_name, available_time):
        self.available_time[pool_name] = available_time / 3600

    def sort_pool_by_utilization(self):
        return sorted(self.pool_utilization.keys(), key=lambda pool_name: self.pool_utilization[pool_name],
                      reverse=True)

    def add_task_statistics(self, task_pools, task_name, total_waiting_time, total_processing_time, total_cost):
        pool_names = task_pools[task_name]
        for r_pool in pool_names:
            pool_name = r_pool['id']
            if pool_name not in self.pool_cost:
                self.pool_cost[pool_name] = (total_cost * self.simulation_duration() / 3600)
                self.total_pool_cost += self.pool_cost[pool_name]
            if pool_name not in self.pool_time:
                self.pool_time[pool_name] = 0

            self.pool_time[pool_name] += total_waiting_time + total_processing_time
            self.total_pool_time += total_waiting_time + total_processing_time

    def resource_utilization_for(self, pool_name):
        return self.pool_utilization[pool_name] if pool_name in self.pool_utilization[pool_name] else 0

    def to_json(self):
        return {
            'pools_info': self.pools_info.to_json(),
            'mean_process_cycle_time': self.mean_process_cycle_time,
            'simulation_start_date': str(self.simulation_start_date) if self.simulation_start_date is not None else None,
            'simulation_end_date': str(self.simulation_end_date) if self.simulation_end_date is not None else None,
            'simulation_time': self.simulation_time,
            'deviation_info': self.deviation_info.to_json(),
            'pool_utilization': self.pool_utilization,
            'pool_time': self.pool_time,
            'pool_cost': self.pool_cost,
            'total_pool_cost': self.total_pool_cost,
            'total_pool_time': self.total_pool_time,
            'available_time': self.available_time
        }
        