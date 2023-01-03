import shutil

experiments = {0: "production",
               1: "purchasing_example",
               2: "government",
               3: "financial",
               4: "consulta_data_mining",
               5: "bpi_2012_edoc",
               6: "bpi_2012",
               7: "bpi_2017",
               8: "credit_application",
               9: "loan_origination"}

bfp = "./test_assets/experiments/"

experiments_file_paths = {
    'production': [bfp + "production/timetable.json",
                   bfp + "production/constraints.json",
                   bfp + "production/model.bpmn"],
    'purchasing_example': [bfp + "purchasing_example/timetable.json",
                           bfp + "purchasing_example/constraints.json",
                           bfp + "purchasing_example/model.bpmn"],
    'government': [bfp + "government/timetable.json",
                   bfp + "government/constraints.json",
                   bfp + "government/model.bpmn"],
    'financial': [bfp + "financial/timetable.json",
                  bfp + "financial/constraints.json",
                  bfp + "financial/model.bpmn"],
    'consulta_data_mining': [bfp + "consulta/timetable.json",
                             bfp + "consulta/constraints.json",
                             bfp + "consulta/model.bpmn"],
    'bpi_2012_edoc': [bfp + "bpi_2012_edoc/timetable.json",
                      bfp + "bpi_2012_edoc/constraints.json",
                      bfp + "bpi_2012_edoc/BPI_2012_Edoc.bpmn"],
    'bpi_2012': [bfp + "bpi_2012/timetable.json",
                 bfp + "bpi_2012/constraints.json",
                 bfp + "bpi_2012/model.bpmn"],
    'bpi_2017': [bfp + "bpi_2017/timetable.json",
                 bfp + "bpi_2017/constraints.json",
                 bfp + "bpi_2017/model.bpmn"],
    'credit_application': [bfp + "credit_application/timetable.json",
                           bfp + "credit_application/constraints.json",
                           bfp + "credit_application/model.bpmn"],
    'loan_origination': [bfp + "loan_origination/timetable.json",
                         bfp + "loan_origination/constraints.json",
                         bfp + "loan_origination/model.bpmn"],
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
