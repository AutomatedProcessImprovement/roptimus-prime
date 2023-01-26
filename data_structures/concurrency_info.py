
class ConcurrencyRatio:
    def __init__(self, c_ratio, m_ratio, c_mean, m_mean):
        self.concurrency_ratio = c_ratio
        self.multitasking_ratio = m_ratio
        self.concurrency_mean = c_mean
        self.multitasking_mean = m_mean


class ConcurrencyInfo:
    def __init__(self):
        # For each task T, how many instances were executed
        # task_instances[T : string] -> instances_count(T) : number
        self.task_instances = dict()
        self.task_concurrency = dict()
        self.resource_multitasking = dict()
        self.concurrency_relations = dict()
        self.multitasking_relations = dict()

        self.concurrency_ratios = dict()
        self.concurrency_graph = dict()

    def update_task_info(self, task_name):
        if task_name not in self.task_instances:
            self.task_instances[task_name] = 0
            self.task_concurrency[task_name] = list()
            self.resource_multitasking[task_name] = list()
        self.task_instances[task_name] += 1

    def init_concurrency_relations(self):
        for k1 in self.task_instances:
            for k2 in self.task_instances:
                if k1 not in self.concurrency_relations:
                    self.concurrency_relations[k1] = dict()
                    self.multitasking_relations[k1] = dict()
                if k2 not in self.concurrency_relations[k1]:
                    self.concurrency_relations[k1][k2] = list()
                    self.multitasking_relations[k1][k2] = list()

    def update_concurrency_info(self, task_name, concurrent_instances, concurrent_resources, relations_info):
        self.task_concurrency[task_name].append(concurrent_instances)
        self.resource_multitasking[task_name].append(concurrent_resources)
        for element_name in relations_info[task_name]:
            self.concurrency_relations[task_name][element_name].append(relations_info[task_name][element_name][0])
            self.multitasking_relations[task_name][element_name].append(relations_info[task_name][element_name][1])

    def calculate_concurrency_info(self):
        for task_name in self.resource_multitasking:
            self.concurrency_ratios[task_name] = self._calculate_ratios(task_name, self.task_concurrency[task_name],
                                                                        self.resource_multitasking[task_name])
        for t1 in self.task_instances:
            for t2 in self.task_instances:
                self.concurrency_graph[t1] = dict()
                self.concurrency_graph[t1][t2] = self._calculate_ratios(t1, self.concurrency_relations[t1][t2],
                                                                        self.multitasking_relations[t1][t2])

    def _calculate_ratios(self, task_name, concurrency_list, muultitasking_list):
        total_sum = 0
        total_resources = 0
        total_concurrency = 0
        total_multitasking = 0
        for i in range(0, len(concurrency_list)):
            total_sum += concurrency_list[i]
            if concurrency_list[i] > 0:
                total_concurrency += 1
            if muultitasking_list[i] > 0:
                total_multitasking += 1
            total_resources += muultitasking_list[i]

        return ConcurrencyRatio(
            total_concurrency / self.task_instances[task_name],
            total_multitasking / self.task_instances[task_name],
            total_sum / self.task_instances[task_name],
            total_resources / self.task_instances[task_name]
        )

    def print_concurrency_ratios(self):
        for task_name in self.resource_multitasking:
            print("%s: " % task_name)
            print(" Concurrency Ratio  %2f" % self.concurrency_ratios[task_name].concurrency_ratio)
            print(" Concurrency Mean %2f" % self.concurrency_ratios[task_name].concurrency_mean)
            print(" Multitasking Ratio %2f" % self.concurrency_ratios[task_name].multitasking_ratio)
            print(" Multitasking Mean %2f" % self.concurrency_ratios[task_name].multitasking_mean)
            print("-------------------------------------------------------")

    def print_concurrency_graph(self):
        for t1 in self.concurrency_graph:
            for t2 in self.concurrency_graph[t1]:
                print("%s: -> %s" % (t1, t2))
                print(" Concurrency Ratio  %2f" % self.concurrency_graph[t1][t2].concurrency_ratio)
                print(" Concurrency Mean %2f" % self.concurrency_graph[t1][t2].concurrency_mean)
                print(" Multitasking Ratio %2f" % self.concurrency_graph[t1][t2].multitasking_ratio)
                print(" Multitasking Mean %2f" % self.concurrency_graph[t1][t2].multitasking_mean)
                print("-------------------------------------------------------")
