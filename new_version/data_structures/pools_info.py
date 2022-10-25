
class PoolInfo:
    def __init__(self, resource_map, task_pools):
        self.pools = resource_map
        self.task_pools = task_pools
        # TODO new way to represent pools
        self.id = '_'.join(str(v.bpm_resource_name) for v in self.pools.values())
        # TODO pool cost and ho to work with "total resources????"
        self.pools_total_cost = 1
        self.total_resoures = 1
        # for pool in self.pools:
        #     self.total_resoures += self.pools[pool].total_amount
        #     self.pools_total_cost += self.pools[pool].get_total_cost()

    def get_pool_for(self, task_name):
        if task_name in self.task_pools:
            return self.task_pools[task_name]


# class Resource:
#     def __init__(self, pool_id, name):
#         self.cost_per_hour = 0
#         self.total_amount = 0
#         self.id = pool_id
#         self.name = name
#
#     def set_cost(self, increase_by):
#         self.cost_per_hour += increase_by
#
#     def set_total_amount(self, increase_by):
#         self.total_amount += increase_by
#
    # def get_total_cost(self):
    #     return self.cost_per_hour * self.total_amount / 3600
#
#     def clone(self):
#         new_pool = Resource(self.id, self.name)
#         new_pool.total_amount = self.total_amount
#         new_pool.cost_per_hour = self.cost_per_hour
