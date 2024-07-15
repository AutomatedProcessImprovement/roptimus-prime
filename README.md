# Optimos

## UI Repository
The UI is part of the [pix-portal repository](https://github.com/AutomatedProcessImprovement/pix-portal). The source code of the constraints settings page can be found [here](https://github.com/AutomatedProcessImprovement/pix-portal/tree/optimos-only/frontend/pix-web-ui/app/routes/projects.%24projectId.%24processingType/components/optimos), the source code of results page [here](https://github.com/AutomatedProcessImprovement/pix-portal/tree/optimos-only/frontend/pix-web-ui/app/routes/optimos.results.%24requestId).

The source code for the backend service lies in [this folder](https://github.com/AutomatedProcessImprovement/pix-portal/tree/optimos-only/backend/workers/optimos), although this only handles the interaction with the messaging queue and _api-server_, the actual optimization engine called is found in this repository.

## Using Optimos in the Web

1. Go to the [Optimos Web Interface](https://pix-w1.cloud.ut.ee/)
2. Create an Account. Please enter a real email address as you will need to confirm your account. If you want to keep your anonymity, you can use a temporary email address (e.g. [temp-mail.org](https://temp-mail.org/en/)), we do **not** block these.
3. Create a Project
4. Upload your Assets:
   1. Click on "Upload assets"
   2. Here you could upload the following files:
        - **Required:** Upload a Simulation Parameters (also known as Timetable, JSON-File)
        - **Required:** Upload a BPMN Model (XML-File)
        - **Optional**: Upload a Optimos Constraint Parameters (see below for format, JSON-File)
        - _You may also upload a zip file containing any of the above files_
        - _If you haven't got any of the required files, you can e.g. generate them from an event log by using a tool like [Simod](https://github.com/AutomatedProcessImprovement/Simod)._
    3. If you haven't uploaded Optimos Constraint Parameters, you can generate an initial set by only selecting the Simulation Model and press "Generate Constraints"
 5. Select both the Simulation Model and the Optimos Constraint Parameters in the left side bar, you should then see the optimos settings
 6. Modify the constraints to your liking, check the validation tab to see if your constraints are valid
 7. Press "Start Optimization"
 8. Wait a few seconds for the optimization to start, you can immediately open the current iteration to see the progress
 9. **Don't be surprised** that there will be more Solutions than the amount of iterations you have set. This is due to the fact that the algorithm tries multiple solutions per iteration.
 10. Wait for the optimization to finish. You can always come back to the project later to see the results.
 11. Click "Show Results" to see the results of the optimization. You can scroll through the results and download the updated timetable ("Parameters") for each solution. You can also download the constraints here, although they of course haven't changed.

    

## Running Optimos on your Machine

### Step-By-Step Guide to running Optimos on it's own (Command-Line)

#### Pre-requisites
1. Install Python 3.9 / 3.10, refer to the [official website](https://www.python.org/downloads/) for installation instructions
2. Install Poetry (`pip install poetry`)
3. Clone the repository (`git clone https://github.com/AutomatedProcessImprovement/roptimus-prime`)
4. Install the dependencies (`poetry install`)
5. You are ready to go.

#### Running Optimos
_Its assumed that you run the following commands in the root directory of the repository._
1. You can run `python optimos.py --help` to see a list of available commands
2. For example to run a simple optimization task, you can run
```bash
python optimos.py start-optimization \
--bpmn_path test_assets/experiments/financial/model.bpmn \
--constraints_path test_assets/experiments/financial/constraints.json \
--sim_params_path test_assets/experiments/financial/timetable.json \
--total_iterations 100 \
--algorithm HC-FLEX
```
3. You can find different experiments in the `test_assets/experiments` folder. You can run them by changing the paths in the command above. The files used in the demo video can be found in the `test_assets/demo` folder.
4. In the Output look for an "OUTPUT" Section, there you find the `Optimos Base Path`. In there the following files might be of interest:
   - `output/explored_allocations/DEFAULT_[...].csv` Contains the progress of the optimization in a compact csv format. It shows some selected statistics of each iteration & resource.
   - `output/simulation_resultsDEFAULT_full.cv` & `output/simulation_resultsDEFAULT_median.csv` contain the statistics of every iteration tried
   - `solutions/[SOLUTION_ID]` contains the timetable, constraints & model for each solution. Look up your chosen solution here, to get the optimized timetable.


### Step-By-Step Guide to running Optimos including UI
1. Install Docker and Docker-Compose, refer to the [official website](https://docs.docker.com/get-docker/) for installation instructions
2. Clone the [pix-portal](https://github.com/AutomatedProcessImprovement/pix-portal) repository (`git clone https://github.com/AutomatedProcessImprovement/pix-portal.git`)
3. Create the following secrets:
   - `frontend/pix-web-ui/.session.secret`
   - `backend/services/api-server/.superuser_email.secret`
   - `backend/services/api-server/.system_email.secret`
   - `backend/services/api-server/.superuser_password.secret`
   - `backend/services/api-server/.key.secret`
   - `backend/services/api-server/.system_password.secret`
   - _For local development/testing you can just fill them with example values, e.g. "secret"_
   - If you want to send out mails you also need to create secrets:  `backend/workers/mail/.secret_gmail_username` & `backend/workers/mail/.secret_gmail_app_password`; 
   Those are the credentials for the mail account that sends out the mails. If you don't want to send out mails, you can ignore this step.
4. Create the following `.env` files:
    - `backend/workers/mail/.env`
    - `backend/workers/kronos/.env`
    - `backend/workers/simulation-prosimos/.env`
    - `backend/workers/bps-discovery-simod/.env`
    - `backend/workers/optimos/.env`
    - `backend/services/api-server/.env`
    - `backend/services/kronos/.env`
    - _You will find a `.env.example` file in each of the folders, you can copy this file and rename it to `.env`_
5. Run `docker-compose up --build` in the root directory of the pix-portal repository
6. _This will take some time_
7. Open your browser and go to `localhost:9999`, now you can refer to the section above to use the web interface.

---
# General Description

![build](https://github.com/AutomatedProcessImprovement/roptimus-prime/actions/workflows/python.yml/badge.svg)
![release](https://github.com/AutomatedProcessImprovement/roptimus-prime/actions/workflows/release-pypi.yml/badge.svg)
![version](https://img.shields.io/github/v/tag/AutomatedProcessImprovement/roptimus-prime)

__Resource allocation and optimisation of Business Processes with Differentiated Resources__

Optimos is a Business Process Optimisation Engine that support differentiated resources. The notion of a resource pool is replaces with resource profiles. 
Resource profiles are unique to each resource and entail the calendar, the tasks assigned and, differentiated performance parameters relevant to the resource.

This repository contains the implementation and experimental results of a multi-objective optimisation approach to compute a set of Pareto-optimal resource allocation for a given business process, minimising the resource cost and time.

The source code includes two variants of the hill-climbing algorithm, named __HC-STRICT__ and __HC-FLEX__. 
Future work may include the implementation of the tabu-search algorithm.

Optimos makes use of the [Prosimos](https://github.com/AutomatedProcessImprovement/Prosimos/commit/3eae6c5e322a534bb47068f6373e9af572268c8f) simulation engine.


## File Formats

Optimos in its command-line format requires three files to perform an optimisation:
- BPMN Model
- Simulation parameters (JSON format - Refer to [Prosimos](https://github.com/AutomatedProcessImprovement/Prosimos/tree/main) for more information about the format)
- Constraint parameters (JSON format)


### Resource constraint parameters
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
