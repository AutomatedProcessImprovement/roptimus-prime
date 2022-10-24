from new_version.data_structures.concurrency_info import ConcurrencyInfo


class Event:
    def __init__(self, case_id, task_name, resource, timestamp):
        self.case_id = case_id
        self.task_name = task_name
        self.resource = resource
        self.start_timestamp = timestamp
        self.end_timestamp = ''

    def add_end_timestamp(self, end_timestamp):
        self.end_timestamp = end_timestamp

    def compare_to(self, event):
        return self.end_timestamp > event.start_timestamp and self.start_timestamp < event.end_timestamp \
               or (self.start_timestamp == event.start_timestamp and self.end_timestamp == event.end_timestamp)

    def equal(self, event):
        return self.case_id == event.case_id and self.task_name == event.task_name and self.resource == event.resource \
               and self.start_timestamp == event.start_timestamp and self.end_timestamp == event.end_timestamp


class EventLogInfo:
    def __init__(self):
        self.cycle_time = 0
        self.max_cycle_time = 0
        self.total_cost = 0
        self.log_events = list()
        self.task_resources_count = dict()
        self.concurrency_info = ConcurrencyInfo()
        self.task_similarity_graph = dict()
        self.execution_start_date = None
        self.execution_end_date = None
        self.total_resources = 0
        self.cumulative_task_execution_time = 0
        self.task_execution_times = dict()

    def execution_duration(self):
        return (self.execution_end_date - self.execution_start_date).total_seconds()

    def update_cyle_time(self, cycle_time):
        self.cycle_time = cycle_time

    def update_cost(self, cost):
        self.total_cost = cost

    def task_instances(self):
        return self.concurrency_info.task_instances

    def add_event(self, event):
        self.log_events.append(event)
        self.concurrency_info.update_task_info(event.task_name)
        if event.task_name not in self.task_resources_count:
            self.task_resources_count[event.task_name] = dict()
        if event.resource not in self.task_resources_count[event.task_name]:
            self.task_resources_count[event.task_name][event.resource] = 0
        self.task_resources_count[event.task_name][event.resource] += 1
        execution_time = (event.end_timestamp - event.start_timestamp).total_seconds()
        self.cumulative_task_execution_time += execution_time
        if event.task_name not in self.task_execution_times:
            self.task_execution_times[event.task_name] = 0
        self.task_execution_times[event.task_name] += execution_time

    def calculate_resource_utilization(self, task_pools, reverse=False):
        pool_execution_times = dict()
        for task_name in task_pools:
            if task_pools[task_name] not in pool_execution_times:
                pool_execution_times[task_pools[task_name]] = 0
            if task_name in self.task_execution_times:
                pool_execution_times[task_pools[task_name]] += self.task_execution_times[task_name]
        resource_utilization = dict()
        for resource_id in pool_execution_times:
            utilization = pool_execution_times[resource_id] / self.cumulative_task_execution_time
            resource_utilization[resource_id] = 1 - utilization if reverse else utilization
        return resource_utilization

    def calculate_event_concurrency(self):
        start_sorting = sorted(self.log_events, key=lambda event_info: event_info.start_timestamp)
        end_sorting = sorted(self.log_events, key=lambda event_info: event_info.end_timestamp)
        self.concurrency_info.init_concurrency_relations()

        i = 0
        for event in start_sorting:
            s_candidates = _neighbours_search(start_sorting, i)
            j = _binary_search(end_sorting, start_sorting[i])
            candidates = _neighbours_search(end_sorting, j)
            candidates.intersection_update(s_candidates)
            resources = 0
            relations_count = dict()
            relations_count[event.task_name] = dict()

            for e in candidates:
                if e.task_name not in relations_count[event.task_name]:
                    relations_count[event.task_name][e.task_name] = [0, 0]
                relations_count[event.task_name][e.task_name][0] += 1
                if event.resource == e.resource:
                    resources += 1
                    relations_count[event.task_name][e.task_name][1] += 1
            self.concurrency_info.update_concurrency_info(event.task_name, len(candidates), resources, relations_count)
            i += 1
        self.concurrency_info.calculate_concurrency_info()

    def calculate_task_similarity(self):
        self.task_similarity_graph = _calculate_similarity(self.task_instances(), self.task_resources_count)

    def calculate_pool_similarity(self, task_pools):
        merged_resources = dict()
        for task_name in self.task_instances():
            pool_name = task_pools[task_name]
            if pool_name not in merged_resources:
                merged_resources[pool_name] = dict()
            for r in self.task_resources_count[task_name]:
                if r not in merged_resources[pool_name]:
                    merged_resources[pool_name][r] = 0
                merged_resources[pool_name][r] += self.task_resources_count[task_name][r]

        return _calculate_similarity(merged_resources, merged_resources)

    def print_task_similarity(self, simod_info):
        for t1 in self.task_similarity_graph:
            for t2 in self.task_similarity_graph[t1]:
                print("%s: -> %s" % (t1, t2))
                print("%s: -> %s" % (simod_info.get_pool_for(t1), simod_info.get_pool_for(t2)))
                print(" Similarity Index  %2f" % self.task_similarity_graph[t1][t2])
                print("-------------------------------------------------------")


def _check_and_update(e1, e2, candidates):
    if e1.compare_to(e2):
        if not e1.equal(e2):
            candidates.add(e2)
        return True
    return False


def _neighbours_search(sorted_list, e_index):
    event = sorted_list[e_index]
    j = e_index + 1
    candidates = set()
    while e_index >= 0 and _check_and_update(event, sorted_list[e_index], candidates):
        e_index -= 1
    while j < len(sorted_list) and _check_and_update(event, sorted_list[j], candidates):
        j += 1
    return candidates


def _binary_search(end_sorting, event):
    low = 0
    high = len(end_sorting) - 1
    while low <= high:
        mid = (high + low) // 2
        if end_sorting[mid].end_timestamp < event.end_timestamp:
            low = mid + 1
        elif end_sorting[mid].end_timestamp > event.end_timestamp:
            high = mid - 1
        else:
            i = 0
            init = [mid, mid - 1]
            to_increase = [1, -1]
            for j in init:
                while end_sorting[j].end_timestamp == event.end_timestamp:
                    if event.equal(end_sorting[j]):
                        return j
                    j += to_increase[i]
                i += 1
    return -1


def _calculate_similarity(frequency_map, resource_count):
    similarity_graph = dict()
    for t1 in frequency_map:
        similarity_graph[t1] = dict()
        for t2 in frequency_map:
            match_count = 0
            total_count = 0
            for r in resource_count[t1]:
                total_count += resource_count[t1][r]
                if r in resource_count[t2]:
                    match_count += min(resource_count[t1][r], resource_count[t2][r])
            similarity_graph[t1][t2] = match_count / total_count
    return similarity_graph
