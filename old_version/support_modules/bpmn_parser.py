import xml.etree.ElementTree as ET

from new_version.data_structures.pools_info import PoolInfo
from new_version.data_structures.pools_info import Resource
from new_version.support_modules.file_manager import temp_bpmn_file

bpmn_schema_url = 'http://www.omg.org/spec/BPMN/20100524/MODEL'
camunda_schema_url = 'http://camunda.org/schema/1.0/bpmn'
bpmn_element_ns = {'xmlns': bpmn_schema_url}
camunda_element_ns = {'xmlns': camunda_schema_url} # NOT USED ANYWHERE
simod_ns = {'qbp': 'http://www.qbp-simulator.com/Schema201212'}


def update_resource_pools(resource_pools={}, task_pools={}, task_ids={}):
    tree = ET.parse(temp_bpmn_file)
    root = tree.getroot()

    if len(task_pools) > 0:
        simod_elements = root.find('xmlns:process', bpmn_element_ns).find('xmlns:extensionElements', bpmn_element_ns).find("qbp:elements", simod_ns)
        for e_inf in simod_elements:
            if e_inf.attrib["elementId"] in task_ids and task_ids[e_inf.attrib["elementId"]] in task_pools:
                e_name = task_ids[e_inf.attrib["elementId"]]
                resource = e_inf.find("qbp:resourceIds", simod_ns).find("qbp:resourceId", simod_ns)
                resource.text = resource_pools[task_pools[e_name]]

    if len(resource_pools) > 0:
        bpmn_resources = root.find('xmlns:process', bpmn_element_ns).find('xmlns:extensionElements', bpmn_element_ns).find("qbp:processSimulationInfo", simod_ns).find("qbp:resources", simod_ns)
        for resource in bpmn_resources:
            resource.attrib["totalAmount"] = str(resource_pools[resource.attrib["name"]].total_amount)
        tree.write(temp_bpmn_file)


def update_resource_cost(resource_costs={}):
    tree = ET.parse(temp_bpmn_file)
    root = tree.getroot()

    bpmn_resources = root.find('xmlns:process', bpmn_element_ns).find('xmlns:extensionElements', bpmn_element_ns).find("qbp:processSimulationInfo", simod_ns).find("qbp:resources", simod_ns)
    for resource in bpmn_resources:
        # resource.attrib["costPerHour"] = "1" if len(resource_costs) == 0 \
        #     else str(resource_costs[resource.attrib["name"]])
        pass
    tree.write(temp_bpmn_file)


def parse_simulation_model():
    tree = ET.parse(temp_bpmn_file)
    root = tree.getroot()
    # descendants = list(root.iter())
    simod_root = root.find('xmlns:process', bpmn_element_ns).find('xmlns:extensionElements', bpmn_element_ns).find('qbp:processSimulationInfo', simod_ns)
    # simod_root = root.find("qbp:processSimulationInfo", simod_ns)

    # Extracting Task info [task_id => task_name] from simulation model
    task_ids = dict()
    for process in root.findall('xmlns:process', bpmn_element_ns):
        for task in process.findall('xmlns:task', bpmn_element_ns):
            task_ids[task.attrib["id"]] = task.attrib["id"]

    # Extracting Resource Pools Info from Simulation model (pool_name, pool_id, pool_cost, pool_resource_count)
    resource_pools = dict()
    resource_ids = dict()
    bpmn_resources = simod_root.find("qbp:resources", simod_ns)
    for resource in bpmn_resources:
        pool = Resource(resource.attrib["id"], resource.attrib["name"])
        pool.set_total_amount(int(resource.attrib["totalAmount"]))
        pool.set_cost(int(resource.attrib["costPerHour"]))
        resource_pools[pool.name] = pool
        resource_ids[pool.id] = pool.name

    # Extracting relation task - resource pool
    simod_elements = simod_root.find("qbp:elements", simod_ns)
    task_pools = dict()
    for e_inf in simod_elements:
        task_pools[task_ids[e_inf.attrib["elementId"]]] =\
            resource_ids[e_inf.find("qbp:resourceIds", simod_ns).find("qbp:resourceId", simod_ns).text]
    return PoolInfo(resource_pools, task_pools)
