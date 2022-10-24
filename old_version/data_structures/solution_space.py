
class SolutionSpace:
    def __init__(self, it_number=0, execution_cost=0.0, cycle_time=0.0, time_deviation=0.0, cost_deviation=0.0,
                 simulation_duration=0.0):
        self.it_number = it_number
        self.median_execution_cost = execution_cost
        self.median_cycle_time = cycle_time
        self._simulation_duration = simulation_duration
        self.deviation_info = DeviationInfo(time_deviation, cost_deviation)

    def cycle_time(self):
        return self.median_cycle_time

    def simulation_duration(self):
        return self._simulation_duration

    def execution_cost(self):
        return self.median_execution_cost


class ResourceInfo:
    def __init__(self, resource_name, resource_count, resource_utilization, cost_per_unit):
        self.resource_name = resource_name
        self.resource_count = resource_count
        self.resource_utilization = resource_utilization
        self.cost_per_unit = cost_per_unit


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
