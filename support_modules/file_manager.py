import csv
import os
import shutil
import tempfile
from datetime import datetime
from typing import Dict, Optional
from data_structures.iteration_info import IterationInfo
from data_structures.pools_info import PoolInfo
from data_structures.simulation_info import SimulationInfo
from data_structures.solution_space import SolutionSpace, DeviationInfo
from data_structures.solution_space import ResourceInfo


date_format = "%Y-%m-%d %H:%M:%S.%f%z"
date_format_1 = "%Y-%m-%d %H:%M:%S%z"
# date_format_1 = "%Y-%m-%d %H:%M:%S"

prosimos_file_paths = {
    'credit_application_diff': [
        './test_assets/credit_application_diff.bpmn',
        './test_assets/credit_application_diff.json',
        './test_assets/log_demo_filtered_opt.xes'
    ],
    'credit_application_undiff': [
        './test_assets/credit_application_undiff.bpmn',
        './test_assets/credit_application_undiff.json',
        './test_assets/log_demo_filtered_opt.xes'
    ]
}

xes_simodbpmn_file_paths = {
    'purchasing_example': ['./input_files/xes_files/PurchasingExample.xes',
                           './input_files/bpmn_simod_models/PurchasingExample.bpmn'],
    'production': ['./input_files/xes_files/production.xes',
                   './input_files/bpmn_simod_models/model.bpmn'],
    'insurance': ['./input_files/xes_files/insurance.xes',
                  './input_files/bpmn_simod_models/insurance.bpmn'],
    'call_centre': ['./input_files/xes_files/callcentre.xes',
                    './input_files/bpmn_simod_models/callcentre.bpmn'],
    'bpi_challenge_2012': ['./input_files/xes_files/BPI_Challenge_2012_W_Two_TS.xes',
                           './input_files/bpmn_simod_models/BPI_Challenge_2012_W_Two_TS.bpmn'],
    'bpi_challenge_2017_filtered': ['./input_files/xes_files/BPI_Challenge_2017_W_Two_TS_filtered.xes',
                                    './input_files/bpmn_simod_models/BPI_Challenge_2017_W_Two_TS_filtered.bpmn'],
    'bpi_challenge_2017': ['./input_files/xes_files/BPI_Challenge_2017_W_Two_TS.xes',
                           './input_files/bpmn_simod_models/BPI_Challenge_2017_W_Two_TS.bpmn'],
    'consulta_data_mining': ['./input_files/xes_files/ConsultaDataMining201618.xes',
                             './input_files/bpmn_simod_models/ConsultaDataMining201618.bpmn']
}

BASE_FOLDER = os.path.abspath(os.path.join(tempfile.gettempdir(), 'roptimos'))
TMP_FOLDER = os.path.abspath(os.path.join(BASE_FOLDER,'temp'))
OUTPUT_FOLDER = os.path.abspath(os.path.join(BASE_FOLDER,'output'))
SOLUTIONS_FOLDER = os.path.abspath(os.path.join(BASE_FOLDER,'solutions'))
EXPERIMENTS_PLOTS_PATH = os.path.abspath(os.path.join(OUTPUT_FOLDER, 'experiment_stats'))
EXPLORED_ALLOCATIONS_PATH = os.path.abspath(os.path.join(OUTPUT_FOLDER, 'explored_allocations'))
SIMULATION_RESULTS_PATH = os.path.abspath(os.path.join(OUTPUT_FOLDER, 'simulation_results'))

folders = [
    TMP_FOLDER,
    OUTPUT_FOLDER,
    SOLUTIONS_FOLDER,
    EXPERIMENTS_PLOTS_PATH,
    EXPLORED_ALLOCATIONS_PATH,
    SIMULATION_RESULTS_PATH
]
for folder in folders:
    os.makedirs(folder, exist_ok=True)

BACKUP_BPMN_PATH = os.path.abspath(os.path.join(TMP_FOLDER, 'CopiedModel.bpmn'))



def reset_file_information(log_name):
    pass

def save_simulation_results(log_name, pools_info, simulation_list, median_simulation):
    try:
        with open(SIMULATION_RESULTS_PATH + ("%s_full.csv" % log_name), mode='a', newline='') as full_csv_file:
            with open(SIMULATION_RESULTS_PATH + ("%s_median.csv" % log_name), mode='a', newline='') as median_csv_file:
                update_simulation_files(pools_info, full_csv_file, median_csv_file, simulation_list, median_simulation)
    except IOError:
        with open(SIMULATION_RESULTS_PATH + ("\\%s_full.csv" % log_name), mode='w', newline='') as full_csv_file:
            with open(SIMULATION_RESULTS_PATH + ("\\%s_median.csv" % log_name), mode='w', newline='') as median_csv_file:
                update_simulation_files(pools_info, full_csv_file, median_csv_file, simulation_list, median_simulation)


def update_simulation_files(pools_info, full_csv_file, median_csv_file, simulation_list, median_simulation):
    save_one_simulation_result(pools_info, median_csv_file, median_simulation)
    for simulation_info in simulation_list:
        save_one_simulation_result(pools_info, full_csv_file, simulation_info)


def save_one_simulation_result(pools_info, csv_file, simulation_info):
    csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow([str(pools_info.id),
                         str(simulation_info.mean_process_cycle_time),
                         str(simulation_info.pools_info.pools_total_cost),
                         str(simulation_info.simulation_start_date),
                         str(simulation_info.simulation_end_date),
                         str(simulation_info.simulation_time),
                         str(simulation_info.deviation_info.p_cycle_time_deviation),
                         str(simulation_info.deviation_info.p_execution_duration_deviation),
                         str(simulation_info.total_pool_cost),
                         str(simulation_info.total_pool_time)])
    csv_writer.writerow(['utilization'])
    for key in pools_info.pools:
        csv_writer.writerow([str(pools_info.id),
                             str(key),
                             str(simulation_info.pool_utilization[key])])
    csv_writer.writerow(['pool_time_cost'])
    for key in pools_info.pools:
        csv_writer.writerow([str(pools_info.id),
                             str(key),
                             str(simulation_info.pool_time[key]),
                             str(simulation_info.pool_cost[key])])
    csv_writer.writerow([])


def load_simulation_result(log_name: str, pools_info: PoolInfo):
    try:
        simulation_info = SimulationInfo(pools_info)
        with open(SIMULATION_RESULTS_PATH + ("\\%s_median.csv" % log_name), mode='r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            file_section = 0
            for row in csv_reader:
                if len(row) > 0:
                    if row[0] == pools_info.id:
                        if file_section == 0:
                            simulation_info.mean_process_cycle_time = float(row[1])
                            simulation_info.simulation_start_date = parse_date(row[3])
                            simulation_info.simulation_end_date = parse_date(row[4])
                            simulation_info.simulation_time = float(row[5])
                            simulation_info.deviation_info = DeviationInfo(float(row[6]), float(row[7]))
                            simulation_info.total_pool_cost = float(row[8])
                            simulation_info.total_pool_time = float(row[9])
                            file_section = 1
                        elif file_section == 1:
                            simulation_info.pool_utilization[row[1]] = float(row[2])
                        elif file_section == 2:
                            simulation_info.pool_time[row[1]] = float(row[2])
                            simulation_info.pool_cost[row[1]] = float(row[3])
                    elif file_section == 1 and row[0] == 'pool_time_cost':
                        file_section = 2
                elif file_section == 2:
                    return simulation_info
            return None
    except IOError:
        return None


def duration(start_date, end_date):
    return (parse_date(end_date) - parse_date(start_date)).total_seconds()


def parse_date(date_str):
    print(date_str)
    try:
        return datetime.strptime(date_str, date_format)
    except ValueError:
        return datetime.strptime(date_str, date_format_1)


def create_genetic_stats_files(log_name):
    with open(EXPLORED_ALLOCATIONS_PATH + ("\\%s_nsga2_simulation_info.csv" % log_name), mode='w', newline='') as simul_csv_file:
        with open(EXPLORED_ALLOCATIONS_PATH + ("\\%s_nsga2_pools_info.csv" % log_name), mode='w', newline='') as pools_csv_file:
            simul_csv_writer = csv.writer(simul_csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            write_stats_header(simul_csv_writer)
            pools_csv_writer = csv.writer(pools_csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            write_pools_info_header(pools_csv_writer)


def update_genetic_stats_file(log_name, it_number, simulation_info, pools_info):
    with open(EXPLORED_ALLOCATIONS_PATH + ("\\%s_nsga2_simulation_info.csv" % log_name), mode='a', newline='') as simul_csv_file:
        with open(EXPLORED_ALLOCATIONS_PATH + ("\\%s_nsga2_pools_info.csv" % log_name), mode='a', newline='') as pools_csv_file:
            simulation_csv_writer = csv.writer(simul_csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            write_simulation_info_stats(simulation_csv_writer, it_number, simulation_info, pools_info)

            pools_csv_writer = csv.writer(pools_csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            write_pools_info_stats(pools_csv_writer, it_number, simulation_info, pools_info)


# Method for Hill-Climbing and Tabu Search
def save_stats_file(log_name:str, algorithm_name:str, generated_solutions: Dict[str, IterationInfo], simulation_order:list[str], iteration_count:int):
    with open(EXPLORED_ALLOCATIONS_PATH + ("\\%s_%s.csv" % (log_name, algorithm_name)), mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        csv_writer.writerow(['Total Solutions Generated', "%s" % str(len(generated_solutions))])
        csv_writer.writerow(['Total Iterations', "%s" % str(iteration_count)])

        csv_writer.writerow([])
        write_stats_header(csv_writer)

        for sol_id in simulation_order:
            pools_info = generated_solutions[sol_id].pools_info
            simulation_info = generated_solutions[sol_id].simulation_info
            write_simulation_info_stats(csv_writer, generated_solutions[sol_id].it_number, simulation_info, pools_info)

        csv_writer.writerow([])
        csv_writer.writerow(['Explored Solutions: Pools Info'])
        write_pools_info_header(csv_writer)
        for sol_id in simulation_order:
            pools_info = generated_solutions[sol_id].pools_info
            write_pools_info_stats(csv_writer, generated_solutions[sol_id].it_number,
                                   generated_solutions[sol_id].simulation_info, pools_info)


def write_stats_header(csv_writer):
    csv_writer.writerow(['# Iteration',
                         'Allocation Id',
                         'Execution Cost',
                         'Cycle Time',
                         'Execution Time',
                         'Cycle Time Deviation',
                         'Execution Time Deviation'])


def write_simulation_info_stats(csv_writer, it_number, simulation_info, pools_info):
    csv_writer.writerow([str(it_number),
                         str(pools_info.id),
                         str(simulation_info.execution_cost()),
                         str(simulation_info.cycle_time()),
                         str(simulation_info.simulation_duration()),
                         str(simulation_info.deviation_info.p_cycle_time_deviation),
                         str(simulation_info.deviation_info.p_execution_duration_deviation)])


def write_pools_info_header(csv_writer):
    csv_writer.writerow(['# Iteration',
                         'Pool ID',
                         'Resource',
                         'Allocation',
                         'Utilization',
                         'Single Resource cost per time unit'])


def write_pools_info_stats(csv_writer, it_number, simulation_info, pools_info):
    for resource_name in pools_info.pools:
        pool = pools_info.pools[resource_name]
        csv_writer.writerow([str(it_number),
                             str(pools_info.id),
                             str(resource_name),
                             str(1),
                             str(simulation_info.pool_utilization[resource_name]),
                             str(1)])

StatsType = tuple[dict[str, SolutionSpace], dict[str, list[ResourceInfo]]]
def read_genetic_stats_file(log_name:str) -> Optional[StatsType]:
    try:
        with open(EXPLORED_ALLOCATIONS_PATH + ("\\%s_nsga2_simulation_info.csv" % log_name), mode='r') as simulation_csv_file:
            with open(EXPLORED_ALLOCATIONS_PATH + ("%s_nsga2_pools_info.csv" % log_name), mode='r') as pools_csv_file:
                simulation_csv_reader = csv.reader(simulation_csv_file, delimiter=',')
                pools_csv_reader = csv.reader(pools_csv_file, delimiter=',')
                explored_solutions: Dict[str, SolutionSpace] = dict()
                block_count = False
                for row in simulation_csv_reader:
                    if len(row) < 2:
                        continue
                    if row[0] == '# Iteration':
                        block_count = True
                        continue
                    if block_count:
                        explored_solutions[row[1]] = SolutionSpace(int(row[0]), float(row[2]), float(row[3]),
                                                                   float(row[5]), float(row[6]), float(row[4]))
                resource_pools: Dict[str, list[ResourceInfo]] = dict()
                block_count = False
                for row in pools_csv_reader:
                    if len(row) < 2:
                        continue
                    if row[0] == '# Iteration':
                        block_count = True
                        continue
                    if block_count:
                        if row[1] not in resource_pools:
                            resource_pools[row[1]] = list()
                        resource_pools[row[1]].append(ResourceInfo(row[2], float(row[3]), float(row[4]), float(row[5])))
                return (explored_solutions, resource_pools)
    except IOError:
        return None


def read_stats_file(log_name:str, algorithm_name:str) -> Optional[StatsType]:
    if algorithm_name == 'nsga2':
        return read_genetic_stats_file(log_name)
    try:
        with open(EXPLORED_ALLOCATIONS_PATH + ("\\%s_%s.csv" % (log_name, algorithm_name)), mode='r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            explored_solutions: Dict[str, SolutionSpace] = dict()
            resource_pools:Dict[str, list[ResourceInfo]] = dict()
            block_count = 0
            for row in csv_reader:
                if len(row) < 2:
                    continue
                if row[0] == '# Iteration':
                    block_count += 1
                    continue
                if block_count == 1:
                    explored_solutions[row[1]] = SolutionSpace(int(row[0]), float(row[2]), float(row[3]),
                                                               float(row[5]), float(row[6]), float(row[4]))
                elif block_count == 2:
                    if row[1] not in resource_pools:
                        resource_pools[row[1]] = list()
                    resource_pools[row[1]].append(ResourceInfo(row[2], int(row[3]), float(row[4]), float(row[5])))
            return (explored_solutions, resource_pools)
    except IOError:
        return None

def get_stats_without_writing(generated_solutions: Dict[str, 'IterationInfo'], simulation_order:list[str]) -> Optional[StatsType]:
    explored_solutions: Dict[str, SolutionSpace] = dict()
    resource_pools:Dict[str, list[ResourceInfo]] = dict()

    for sol_id in simulation_order:
        pools_info = generated_solutions[sol_id].pools_info
        simulation_info = generated_solutions[sol_id].simulation_info
        explored_solutions[sol_id] = SolutionSpace(generated_solutions[sol_id].it_number, simulation_info.execution_cost(),
                                                   simulation_info.cycle_time(), simulation_info.deviation_info.p_cycle_time_deviation,
                                                   simulation_info.deviation_info.p_execution_duration_deviation, simulation_info.simulation_duration())
        resource_pools[sol_id] = list()
        for resource_name in pools_info.pools:
            resource_pools[sol_id].append(ResourceInfo(resource_name, 1, simulation_info.pool_utilization[resource_name], 1))
    return (explored_solutions, resource_pools)

def solutions_order_stats_file(log_name, algorithm_name:str)-> Optional[list[str]]:
    try:
        with open(EXPLORED_ALLOCATIONS_PATH + ("\\%s.csv" % algorithm_name), mode='r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            solution_list = list()
            block_count = 0
            for row in csv_reader:
                if len(row) < 2:
                    continue
                if row[0] == '# Iteration':
                    block_count += 1
                    continue
                if block_count == 1:
                    solution_list.append(row[1])
                elif block_count == 2:
                    return solution_list
            return solution_list
    except IOError:
        return None


def initialize_files(save_path, bpmn_path, sim_params_path, constraints_path):
    # Initialize timetable
    shutil.copyfile(sim_params_path,
                    os.path.join(save_path, "timetable_backup.json"))
    # Initialize constraints
    shutil.copyfile(constraints_path,
                    os.path.join(save_path, "constraints_backup.json"))
    # Initialize model
    shutil.copyfile(bpmn_path,
                    os.path.join(save_path, "model_backup.bpmn"))

    # Copy timetable
    shutil.copyfile(os.path.join(save_path, "timetable_backup.json"),
                    os.path.join(save_path, "timetable.json"))
    # Copy constraints
    shutil.copyfile(os.path.join(save_path, "constraints_backup.json"),
                    os.path.join(save_path, "constraints.json"))
    # Copy model
    shutil.copyfile(os.path.join(save_path, "model_backup.bpmn"),
                    os.path.join(save_path, "model.bpmn"))


def reset_after_each_execution(save_path):
    # Assuming the original files are saved under the names :
    # Timetable -> timetable_backup.json
    # Constraints -> constraints_backup.json
    # BPMN -> model_backup.bpmn

    # Copy timetable
    shutil.copyfile(os.path.join(save_path, "timetable_backup.json"),
                    os.path.join(save_path, "timetable.json"))
    # Copy constraints
    shutil.copyfile(os.path.join(save_path, "constraints_backup.json"),
                    os.path.join(save_path, "constraints.json"))
    # Copy model
    shutil.copyfile(os.path.join(save_path, "model_backup.bpmn"),
                    os.path.join(save_path, "model.bpmn"))

    # After resetting ttb, also wipe out json_files dir and ids.txt
    print()
    with open(os.path.abspath(os.path.join(SOLUTIONS_FOLDER,'ids.txt')), 'w'):
        pass
