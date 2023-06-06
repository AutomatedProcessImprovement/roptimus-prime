import shutil

experiments = {0: "production",
               1: "purchasing_example",
               2: "financial",
               3: "consulta",
               4: "bpi2012",
               5: "bpi2017",
               6: "loan_mc_hu",
               7: "loan_mc_lu",
               8: "loan_sc_hu",
               9: "loan_sc_lu",
               10: "simple_model"
               }
               # 7: "government",
               # 8: "bpi_2012_edoc",
               # 9: "credit_application",

bfp = "../test_assets/experiments/"

experiments_file_paths = {
    'production': [bfp + "production/timetable.json",
                   bfp + "production/constraints.json",
                   bfp + "production/model.bpmn"],
    'purchasing_example': [bfp + "purchasing_example/timetable.json",
                           bfp + "purchasing_example/constraints.json",
                           bfp + "purchasing_example/model.bpmn"],
    # 'government': [bfp + "government/timetable.json",
    #                bfp + "government/constraints.json",
    #                bfp + "government/model.bpmn"],
    'financial': [bfp + "financial/timetable.json",
                  bfp + "financial/constraints.json",
                  bfp + "financial/model.bpmn"],
    'consulta': [bfp + "consulta/timetable.json",
                 bfp + "consulta/constraints.json",
                 bfp + "consulta/model.bpmn"],
    # 'bpi_2012_edoc': [bfp + "bpi_2012_edoc/timetable.json",
    #                   bfp + "bpi_2012_edoc/constraints.json",
    #                   bfp + "bpi_2012_edoc/BPI_2012_Edoc.bpmn"],
    'bpi2012': [bfp + "bpi2012/timetable.json",
                 bfp + "bpi2012/constraints.json",
                 bfp + "bpi2012/model.bpmn"],
    'bpi2017': [bfp + "bpi2017/timetable.json",
                 bfp + "bpi2017/constraints.json",
                 bfp + "bpi2017/model.bpmn"],
    # 'credit_application': [bfp + "credit_application/timetable.json",
    #                        bfp + "credit_application/constraints.json",
    #                        bfp + "credit_application/model.bpmn"],
    'loan_mc_hu': [bfp + "loan_mc_hu/timetable.json",
                         bfp + "loan_mc_hu/constraints.json",
                         bfp + "loan_mc_hu/model.bpmn"],
    'loan_mc_lu': [bfp + "loan_mc_lu/timetable.json",
                         bfp + "loan_mc_lu/constraints.json",
                         bfp + "loan_mc_lu/model.bpmn"],
    'loan_sc_hu': [bfp + "loan_sc_hu/timetable.json",
                         bfp + "loan_sc_hu/constraints.json",
                         bfp + "loan_sc_hu/model.bpmn"],
    'loan_sc_lu': [bfp + "loan_sc_lu/timetable.json",
                         bfp + "loan_sc_lu/constraints.json",
                         bfp + "loan_sc_lu/model.bpmn"],
    'simple_model': [bfp + "simple_model/timetable.json",
                             bfp + "simple_model/constraints.json",
                             bfp + "simple_model/model.bpmn"],

}


def reset_after_each_execution(name_of_experiment):
    # Assuming the original files are saved under the names :
    # Timetable -> timetable_backup.json
    # Constraints -> constraints_backup.json
    # BPMN -> model_backup.bpmn

    # Copy timetable
    shutil.copyfile(bfp + name_of_experiment + "/timetable_backup.json",
                    bfp + name_of_experiment + "/timetable.json")
    # Copy constraints
    shutil.copyfile(bfp + name_of_experiment + "/constraints_backup.json",
                    bfp + name_of_experiment + "/constraints.json")
    # Copy model
    shutil.copyfile(bfp + name_of_experiment + "/model_backup.bpmn",
                    bfp + name_of_experiment + "/model.bpmn")

    # After resetting ttb, also wipe out json_files dir and ids.txt
    with open("./json_files/ids.txt", 'w'):
        pass
