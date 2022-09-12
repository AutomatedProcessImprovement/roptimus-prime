import xml.etree.ElementTree as ET
from datetime import datetime

from data_structures.event_log_info import *

date_format = "%Y-%m-%dT%H:%M:%S.%f%z"
date_format_2 = "%Y-%m-%dT%H:%M:%S%z"

formats = [date_format, date_format_2]


def extract_data_from_xes_event_log(log_path):
    try:
        tree = ET.parse(log_path)
        root = tree.getroot()
        ns = {'xes': root.tag.split('}')[0].strip('{')}
        tags = dict(trace='trace',
                    string='string',
                    event='event',
                    date='date')
        traces = root.findall(tags['trace'], ns)

        return _extract_log_info(traces, tags, ns)
    except IOError:
        return None


def _extract_log_info(traces, tags, ns):
    log_info = EventLogInfo()
    i = 0
    total_cycle_time = datetime.max - datetime.max
    total_traces = 0
    resource_list = set()
    for trace in traces:
        total_traces += 1
        started_events = dict()
        caseid = ''
        for string in trace.findall(tags['string'], ns):
            if string.attrib['key'] == 'concept:name':
                caseid = string.attrib['value']
        start_date = None
        end_date = None
        for event in trace.findall(tags['event'], ns):
            task_name = ''
            resource = ''
            state = ''
            for string in event.findall(tags['string'], ns):
                if string.attrib['key'] == 'concept:name':
                    task_name = string.attrib['value']
                if string.attrib['key'] == 'org:resource':
                    resource = string.attrib['value']
                    if resource not in resource_list:
                        resource_list.add(resource)
                if string.attrib['key'] == 'lifecycle:transition':
                    state = string.attrib['value'].lower()
            timestamp = ''
            for date in event.findall(tags['date'], ns):
                if date.attrib['key'] == 'time:timestamp':
                    for fmt in formats: # TODO NEW ADDITION, PARSING TIMESTAMPS WITHOUT %F.
                        try:
                            timestamp = datetime.strptime(date.attrib['value'], fmt)
                        except ValueError:
                            pass
            if task_name not in ['0', '-1', 'Start', 'End', 'start', 'end']:
                start_date = _update_date(start_date, timestamp, 'min')
                end_date = _update_date(end_date, timestamp, 'max')
                log_info.execution_start_date = _update_date(log_info.execution_start_date, timestamp, "min")
                log_info.execution_end_date = _update_date(log_info.execution_end_date, timestamp, "max")
                if state in ["start", "assign"]:
                    started_events[task_name] = Event(caseid, task_name, resource, timestamp)
                elif state == "complete":
                    if task_name in started_events:
                        started_events[task_name].add_end_timestamp(timestamp)
                        log_info.add_event(started_events.pop(task_name))
        total_cycle_time += (end_date - start_date)
        log_info.max_cycle_time = max(log_info.max_cycle_time, (end_date - start_date).total_seconds())
        i += 1
    log_info.update_cyle_time(total_cycle_time.total_seconds() / total_traces)
    log_info.total_resources = len(resource_list)
    return log_info


def _update_date(date, timestamp, is_start):
    if date is None:
        return timestamp
    elif is_start == 'min':
        return min(date, timestamp)
    else:
        return max(date, timestamp)
