import json

from DiffResBP_Simulator.bpdfr_simulation_engine.resource_calendar import int_week_days
from DiffResBP_Simulator.bpdfr_simulation_engine.simulation_properties_parser import parse_resource_calendars


def generate_constraint_file(sim_params_path, out_file):
    with open(sim_params_path) as json_file:
        calendars_map = parse_resource_calendars(json.load(json_file)["resource_calendars"])

        local_constraints = list()
        for c_id in calendars_map:
            c_info = calendars_map[c_id]

            max_daily_work = 0
            max_consecutive_cap = 0
            min_date = None

            for w_day in c_info.work_rest_count:
                max_daily_work = max(max_daily_work, c_info.work_rest_count[w_day][0])

                for c_interv in c_info.work_intervals[w_day]:
                    min_date = c_interv.start if min_date is None else min(min_date, c_interv.start)
                    max_consecutive_cap = max(max_consecutive_cap, c_interv.duration)

            global_constraints = {
                "max_weekly_cap": c_info.total_weekly_work / 3600,
                "max_daily_cap": max_daily_work / 3600,
                "max_consecutive_cap": max_consecutive_cap / 3600,
                "max_shifts_day": 24,
                "max_shifts_week": c_info.total_weekly_work / 3600,
                "is_human": "system" not in c_id.lower()
            }

            daily_start_times = dict()
            never_work_masks = dict()
            always_work_masks = dict()

            min_date_str = min_date.strftime("%H:%M:%S")

            mask_24_hour = 16777215
            for w_day in c_info.work_rest_count:
                c_day = int_week_days[w_day].lower()
                daily_start_times[c_day] = min_date_str if c_info.work_rest_count[w_day][0] > 0 else None
                never_work_masks[c_day] = mask_24_hour if daily_start_times[c_day] is None else 0
                always_work_masks[c_day] = 0  # will keep untouched to always allowing removal

            local_constraints.append({
                "id": c_id,
                "constraints": {
                    "global_constraints": global_constraints,
                    "daily_start_times": daily_start_times,
                    "never_work_masks": never_work_masks,
                    "always_work_masks": always_work_masks
                }
            })

    json_struct = {
        'time_var': 60,
        "max_cap": 9999999999,
        "max_shift_size": 24,
        "max_shift_blocks": 24,
        "hours_in_day": 24,
        'resources': local_constraints}

    # with open(out_file, 'w') as j_writter:
    #     j_writter.write(json.dumps(json_struct, indent=4))

    return json_struct
