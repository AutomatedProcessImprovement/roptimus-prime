
from typing import List, TypedDict, Union


class GlobalConstraints(TypedDict):
    max_weekly_cap: float
    max_daily_cap: float
    max_consecutive_cap: float
    max_shifts_day: int
    max_shifts_week: float
    is_human: bool


class DailyStartTimes(TypedDict):
    monday: Union[int, str]
    tuesday: Union[int, str]
    wednesday: Union[int, str]
    thursday: Union[int, str]
    friday: Union[None, int, str]
    saturday: Union[None, int, str]
    sunday: Union[None, int, str]


class Constraints(TypedDict):
    global_constraints: GlobalConstraints
    daily_start_times: DailyStartTimes
    never_work_masks: DailyStartTimes
    always_work_masks: DailyStartTimes


class ConstraintsResourcesItem(TypedDict):
    id: str
    constraints: Constraints


class ConstraintsType(TypedDict):
    time_var: int
    max_cap: int
    max_shift_size: int
    max_shift_blocks: int
    hours_in_day: int
    resources: List[ConstraintsResourcesItem]
