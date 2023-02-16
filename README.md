Prosimos checkout : 3eae6c5e322a534bb47068f6373e9af572268c8f

# bpm-r-opt
__Silhouetting the Cost-Time Front: Multi-Objective Resource Optimization in Business Processes__

This repository contains the implementation and experimental results of a multi-objective optimization approach to compute a set of Pareto-optimal resource allocations for a given business process minimizing the resource cost and cycle time. 

The source code includes two variants of the hill-climbing algorithm, named __HC-STRICT__ and __HC-FLEX__, one implementation of the tabu-search algorithm named __TS-STRICT__ and one implementation of the genetic algorithm __NSGA-II__. 

Download or clone the source code. Then, to execute the four algorithms and display the experimental results, i.e., which compare the algorithms regarding different metrics, perform the following steps.    

## Input and Output

The algorithms take as input simulation models discovered from event logs. The folder __./input_files/bpmn_simod_models/__ contains the simulation models corresponding to the eight business processes used in the experiments. These models were discovered from event logs (7 of them from real-life business processes) using the tool named Simod (https://github.com/AdaptiveBProcess/Simod). Because several of the event logs used in the experiments are proprietary, we are not sharing them publicly in the repository. Instead, we share the simulation models discovered after anonymizing the event logs. To execute the algorithms on other business processes, add the corresponding simulation models into this folder.

The folder __output_files__ contains the results obtained by each algorithm on each of the business processes used in the experiments. This folder contains four sub-folders. The folder __./output_files/simulation_results/__ includes the results of each simulation performed with the tool BIMP (https://bimp.cs.ut.ee/) used to assess each resource allocation. The folder __./output_files/explored_allocations/__ contains the complete information regarding all the resource allocations obtained on each of the iterations performed by each algorithm. The folder __./output_files/experiment_stats/__ includes all the graphical plots and statistics retrieved by each metric used to assess the algorithms' performance. Finally, the folder __./output_files/bimp_temp_files/__ contains some temporal files produced by the engine BIMP with the simulation results. Note that these folders contain all the data obtained from the experiments. New runs of the algorithms on other models or modifying the existing models' parameters would add new files or modify the existing ones.

> Note that the files in __./output_files/simulation_results/__ were compressed due to their size. For the algorithms to use those files, they must be unzipped. In other words, when running the algorithms, they check in the corresponding unzipped (.csv) file if the simulation results of each generated resource allocation exist. Otherwise, the model is simulated using the engine BIMP. Thus, if the corresponding simulation files do not exist after the first simulation, a new file will be created to memorize (and re-use) the incoming simulation results. 

## Execution Steps

### Prerequisites
- Python 3.8: https://www.python.org/downloads/release/python-380/,
- Java 1.8:   https://www.oracle.com/java/technologies/javase/javase-jdk8-downloads.html.

All the algorithms can be executed by running the Python script __./bpropt.py__ in the root directory. By default, it will print in the terminal the experimental results corresponding to the business process named _production_, which corresponds to the default configuration in the script __./bpropt.py__. 

The following mapping in __./bpropt.py__ restricts which algorithms to execute: 

    to_execute = {'HC-STRICT': False,
                  'HC-FLEX': False,
                  'TS-STRICT': False,
                  'NSGA-II': False,
                  'METRICS': True}

Acccordingly, to selectively execute one or multiple algorithms, set the corresponding values to _True_ before executing the script. Similarly, setting the value of _'METRICS'_ to _True_ will calculate the performance metrics generating the corresponding graphics and statistics once all the algorithms' execution finishes. 

The mapping _experiment_logs_ in __./bpropt.py__ indexes the names of the business processes used in the experimentation. The corresponding file paths to the inputs/outputs of each process are stored in the mapping _xes_simodbpmn_file_paths_ in the file __./support_modules/file_manager.py__. Thus, adding a new process or changing the input/output paths of the existing ones only requires updating those two mappings accordingly.

Finally, from the function _main_, it is possible to execute the selected algorithms on all the processes (remove comments in lines 50-51) indexed in the mapping _experiment_logs_. Also, the selected algorithms can be executed on only one process by specifying its index in _experiment_logs_ as the first input parameter of the function _execute_algorithm_variants_ (line 57). The remaining input parameters of the function _execute_algorithm_variants_ corresponds to the maximum number of resource allocations to generate, the maximum ratio of consecutive non-optimal allocations to generate regarding the maximum amount of allocations, and the last parameter is the number of simulations to run to assess each resource allocation.  






 















