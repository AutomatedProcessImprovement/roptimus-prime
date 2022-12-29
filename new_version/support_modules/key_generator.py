import hashlib


def generate_custom_resource_id(schedule_task_string, resource_name):
    # We will use hashlib to generate a hash from a string of all info required to uniquely identify each allocation
    s = schedule_task_string+'_'+resource_name
    out_hash = hashlib.sha1(str.encode(s)).hexdigest()  # you need to encode the strings into bytes here

    return out_hash

def generate_pools_info_id(ids_list):
    # We will use hashlib to generate a hash from a string of all info required to uniquely identify each allocation
    s = '_'.join(ids_list)
    out_hash = hashlib.sha1(str.encode(s)).hexdigest()  # you need to encode the strings into bytes here

    return out_hash
