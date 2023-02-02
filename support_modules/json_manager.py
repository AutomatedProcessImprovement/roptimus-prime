"""
This class manages the states of the timetable JSON files for each solution that is part of the Pareto.
Each JSON is identifiable through an identifier.
Files will be stored in a separate directory, that can be configured by the user.
"""
import json
import os.path

# ! Always read IDS file first before performing any operation.
import shutil


class JsonManager:
    def __init__(self):
        self.ids = []
        self.path = "./json_files/ids.txt"
        self.base_path_folders = "./json_files/"

    def read_file_with_ids(self):
        new_path = self.path
        new_ids = []

        with open(new_path, "r") as f:
            text = f.read().splitlines()

        for line in text:
            new_ids.append(line)

        self.ids = new_ids
        return self.ids

    def try_create_dir(self, solution_id):
        if not os.path.exists(self.base_path_folders + str(solution_id)):
            os.makedirs(self.base_path_folders + str(solution_id))

    def read_accepted_solution_timetable_to_json_files(self, new_ttb_path, new_cons_path, solution_id):
        ids = self.read_file_with_ids()
        out_ttb_path = self.base_path_folders + str(solution_id) + "/timetable.json"
        out_cons_path = self.base_path_folders + str(solution_id) + "/constraints.json"
        out_model_path = self.base_path_folders + str(solution_id) + "/model.bpmn"

        self.try_create_dir(str(solution_id))

        if solution_id is not None:
            shutil.copyfile(new_ttb_path, out_ttb_path)
            shutil.copyfile(new_cons_path, out_cons_path)
            shutil.copyfile("./temp_files/CopiedModel.bpmn", out_model_path)
            return self.write_new_id_to_file(solution_id)
        else:
            print("Err: Solution ID is of type None.")

    def write_new_id_to_file(self, solution_id):
        ids = self.read_file_with_ids()
        if solution_id not in ids:
            ids.append(solution_id)
        with open(self.path, "w") as f:
            for sol in ids:
                f.write(str(sol) + "\n")
        return True

    def remove_id_from_list(self, solution_id):
        ids = self.read_file_with_ids()
        if solution_id in ids:
            ids.remove(solution_id)

        with open(self.path, "w") as f:
            for sol in ids:
                f.write(str(sol) + "\n")
        return True

    def retrieve_json_from_id(self, solution_id, ttb_path,
                              cons_path):
        ids = self.read_file_with_ids()
        if solution_id in ids:
            shutil.copyfile(self.base_path_folders + str(solution_id) + "/constraints.json", cons_path)
            shutil.copyfile(self.base_path_folders + str(solution_id) + "/timetable.json", ttb_path)
