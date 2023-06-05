# Optimos
__Resource allocation and optimisation of Business Processes with Differentiated Resources__

Optimos is a Business Process Optimisation Engine that support differentiated resources. The notion of a resource pool is replaces with resource profiles. 
Resource profiles are unique to each resource and entail the calendar, the tasks assigned and, differentiated performance parameters relevant to the resource.

This repository contains the implementation and experimental results of a multi-objective optimisation approach to compute a set of Pareto-optimal resource allocation for a given business process, minimising the resource cost and time.

The source code includes two variants of the hill-climbing algorithm, named __HC-STRICT__ and __HC-FLEX__. 
Future work may include the implementation of the tabu-search algorithm.

Optimos makes use of Prosimos: checkout - [3eae6c5e322a534bb47068f6373e9af572268c8f](https://github.com/AutomatedProcessImprovement/Prosimos/commit/3eae6c5e322a534bb47068f6373e9af572268c8f)


## Getting started
#### Prerequisites
For this code repository to function properly, please ensure you have the necessary development environment set up on your system:
- Python 3.8+
- Pip 21.2.3+
- Dependencies mentioned in [requirements.txt](https://github.com/AutomatedProcessImprovement/roptimus-prime/blob/main/requirements.txt)

#### Clone the respository and install dependencies
```
git clone --recurse-submodules https://github.com/AutomatedProcessImprovement/roptimus-prime
```
OR 
```
git clone https://github.com/AutomatedProcessImprovement/roptimus-prime
git submodule update --init --recursive
```

The [PROSIMOS](https://github.com/AutomatedProcessImprovement/Prosimos/tree/main) Simulation Engine will be installed as a submodule. Optimos relies on Prosimos for the simulations required during optimisation.


## Using Optimos

Optimos in its command-line format requires three files to perform an optimisation:
- BPMN Model
- Simulation parameters (JSON format - Refer to [Prosimos](https://github.com/AutomatedProcessImprovement/Prosimos/tree/main) for more information about the format)
- Constraint parameters (JSON format)


#### Resource constraint parameters
The Constraint parameters file is responsible for defining the boundaries of the optimisation task. These parameters are split into the following sections:

- time_var: Represents the granularity of the optimisation task in minutes. This number can either be 60, 30 or 15. E.g., 60 = the day is divided into 24, 60 minute slots. (Only 60 is currently implemented)
- max_cap: Represents the maximum person-hours that can be performed in the process per week. This number is shared by all resources, meaning that in total, the participating resources cannot work more than __X__ hours.
- max_shift_size: ___to be removed___
- hours_in_day: How many days does a day consist of. This parameters is subject to removal
- resources: List of participating resources. Each of these entries has their own subset of parameters, customisable for each entry, such as the max_shifts_day, is_human, ...

__Note__:

- daily_start_times is not implemented currently
- never_work_mask and always_work_mask are integers representing a binary number that, when written in string format: e.g., __111100011__, converts to when the resource can or cannot work, with 1 meaning yes and 0 meaning no in the respective section

Example:
```json
{
    "time_var": 60,
    "max_cap": 9999999999,
    "max_shift_size": 24,
    "max_shift_blocks": 24,
    "hours_in_day": 24,
    "resources": [
        {
            "id": "NOT_SETtimetable",
            "constraints": {
                "global_constraints": {
                    "max_weekly_cap": 78.0,
                    "max_daily_cap": 15.0,
                    "max_consecutive_cap": 14.0,
                    "max_shifts_day": 24,
                    "max_shifts_week": 78.0,
                    "is_human": true
                },
                "daily_start_times": {
                    "monday": "07:00:00",
                    "tuesday": "07:00:00",
                    "wednesday": "07:00:00",
                    "thursday": "07:00:00",
                    "friday": "07:00:00",
                    "saturday": "07:00:00",
                    "sunday": null
                },
                "never_work_masks": {
                    "monday": 8388609,
                    "tuesday": 8388609,
                    "wednesday": 8388609,
                    "thursday": 8388609,
                    "friday": 8388609,
                    "saturday": 8388609,
                    "sunday": 16777215
                },
                "always_work_masks": {
                    "monday": 0,
                    "tuesday": 0,
                    "wednesday": 0,
                    "thursday": 0,
                    "friday": 0,
                    "saturday": 0,
                    "sunday": 0
                }
            }
        }
    ]
}
```

## Output

Optimos as command-line tool is capable of generating multiple output files that give insight into the results of the optimisation task.
The following files are created after a task has finished:

- Comparative metrics: the different approaches are pitched against each other so you can see which approach/algorithm combination performed better overall.
```
['Joint Pareto Size (without MAD): 3 --------------------------------------------------------']
Alg_Name                    #_F_Ev  #_Sol  P_Size  In_JP  !JP  Hyperarea  Hausdorff-Dist  Delta-Sprd  Purity-Rate  Ave_Time                 Ave_cost     Time Metric     Cost Metric
initial (DEFAULT_NAME)      -       -      -       -      -    -          -               -           -            1 day, 9:14:10.546229    112996.14    1.0              1.0        
joint_pareto(DEFAULT_NAME)  19      19     3       3      0    1.0        0.0             0.21386     1.0          1 day, 7:42:18.805322    108078.92    1.04829          1.045497   
HC_STRICT_O_C               19      19     3       3      0    1.0        0.0             0.21386     1.0          1 day, 7:42:18.805322    108078.92    1.04829          1.045497   
------------------------------------------------------
```
- [simulation parameters and constraint parameters of each optimal solution.](./json_files)
- Plots to visualise the Pareto-Distribution and progress of the algorithm (PDF format)

## Executing experiments
The experiments used for testing are available [here](./test_assets/experiments). The experiments are ready to run out-of-the-box. However, there is a clean .zip file available if you wish to reproduce the setup as well.
Keep in mind that the following must always be present for the experiment to run.
- constraints.json
- constraints_backup.json (initially a clean copy of constraints.json)
- model.bpmn
- timetable.json
- timetable_backup.json (initially a clean copy of timetable.json)

You can change the log you wish to run in [main.py](./pareto_algorithms_and_metrics/main.py), function _main()_
The __TO_EXECUTE__ and __APPROACHES__ objects define which algorithm/approach combination you wish to use.

```
TO_EXECUTE = {'HC-STRICT': True, # Hill Climb Strict
              'HC-FLEX': True, # Hill Climb Flex
              'TS-STRICT': False, # Not implemented
              'NSGA-II': False, # Not implemented
              'METRICS': True} # Retrieve the comparative results after execution

APPROACHES = {"only_calendar": True,  # Only perform optimization on schedule level
              "only_add_remove": False,  # Only perform optimization on resource level
              "combined": False,  # Combine schedule + resource optimization -> (WT/Cost/IT | Add/Remove) in 1 iteration
              "first_calendar_then_add_remove": False,  # Only calendar until No_improvement found, then add/remove
              "first_add_remove_then_calendar": False  # Only add/remove until No_improvement found, then calendar
              }
```





 















