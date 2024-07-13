from typing import List, Union

from typing_extensions import TypedDict


class ResourceListItem(TypedDict):
    id: str
    name: str
    cost_per_hour: int
    amount: int
    calendar: str
    assigned_tasks: List[str]


class ResourceProfilesItem(TypedDict):
    id: str
    name: str
    resource_list: List[ResourceListItem]


class DistributionParamsItem(TypedDict):
    value: Union[float, int]


class ArrivalTimeDistribution(TypedDict):
    distribution_name: str
    distribution_params: List[DistributionParamsItem]



TimePeriodsItem = TypedDict("TimePeriodsItem", {
    "from": str,
    "to": str,
    "beginTime": str,
    "endTime": str,
})


class ProbabilitiesItem0(TypedDict):
    path_id: str
    value: float


class GatewayBranchingProbabilitiesItem(TypedDict):
    gateway_id: str
    probabilities: List[ProbabilitiesItem0]


class TimetableResourceItem(TypedDict):
    resource_id: str
    distribution_name: str
    distribution_params: List[DistributionParamsItem]


class TaskResourceDistributionItem(TypedDict):
    task_id: str
    resources: List[TimetableResourceItem]


class ResourceCalendarsItem(TypedDict):
    id: str
    name: str
    time_periods: List[TimePeriodsItem]


class EventDistribution(TypedDict):
    pass


class TimetableType(TypedDict):
    resource_profiles: List[ResourceProfilesItem]
    arrival_time_distribution: ArrivalTimeDistribution
    arrival_time_calendar: List[TimePeriodsItem]
    gateway_branching_probabilities: List[GatewayBranchingProbabilitiesItem]
    task_resource_distribution: List[TaskResourceDistributionItem]
    resource_calendars: List[ResourceCalendarsItem]
    event_distribution: EventDistribution


