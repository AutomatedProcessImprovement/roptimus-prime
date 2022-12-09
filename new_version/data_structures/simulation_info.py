from new_version.data_structures.solution_space import DeviationInfo


class SimulationInfo:
    def __init__(self, pools_info=None):
        self.pools_info = pools_info
        self.mean_process_cycle_time = 0
        self.simulation_start_date = None
        self.simulation_end_date = None
        self.simulation_time = None

        self.deviation_info = DeviationInfo(0.0, 0.0)

        self.pool_utilization = dict()

        self.pool_time = dict()
        self.pool_cost = dict()
        self.total_pool_cost = 0
        self.total_pool_time = 0

        self.available_time = dict()

    def available_time(self):
        return self.available_time

    def cycle_time(self):
        return self.mean_process_cycle_time

    def execution_cost(self):
        return self.pools_info.pools_total_cost * self.simulation_duration()

    def simulation_duration(self):
        return (self.simulation_end_date - self.simulation_start_date).total_seconds()

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
                self.pool_cost[pool_name] = total_cost * self.simulation_duration()
                self.total_pool_cost += self.pool_cost[pool_name]
            if pool_name not in self.pool_time:
                self.pool_time[pool_name] = 0
                self.available_time[pool_name] = 0

            self.pool_time[pool_name] += total_waiting_time + total_processing_time
            self.total_pool_time += total_waiting_time + total_processing_time

    def resource_utilization_for(self, pool_name):
        return self.pool_utilization[pool_name] if pool_name in self.pool_utilization[pool_name] else 0
