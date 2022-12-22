"""
This class manages the states of the timetable JSON files for each solution that is part of the Pareto.
Each JSON is identifiable through an identifier.
Files will be stored in a separate directory, that can be configured by the user.
"""
import json
import os.path


# ! Always read IDS file first before performing any operation.

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
            print("Dir created")
        else:
            print("Dir already exists")

    def read_accepted_solution_timetable_to_json_files(self, new_ttb_path, new_cons_path, solution_id):
        ids = self.read_file_with_ids()
        if new_ttb_path == "":
            new_ttb_path = "./test_assets/production/sim_json.json"
        if new_cons_path == "":
            new_cons_path = "./test_assets/production/constraints.json"

        out_ttb_path = self.base_path_folders + str(solution_id) + "/timetable.json"
        out_cons_path = self.base_path_folders + str(solution_id) + "/constraints.json"

        self.try_create_dir(str(solution_id))

        if solution_id is not None:
            with open(new_ttb_path, "r") as f:
                info = json.load(f)
                with open(out_ttb_path, "w") as o:
                    o.write(json.dumps(info, indent=4))
            with open(new_cons_path, "r") as f:
                info = json.load(f)
                with open(out_cons_path, "w") as o:
                    o.write(json.dumps(info, indent=4))
                    return self.write_new_id_to_file(solution_id)
        print("Err: Solution ID is of type None.")

    def write_new_id_to_file(self, solution_id):
        ids = self.read_file_with_ids()
        if solution_id not in ids:
            ids.append(solution_id)
        print(ids)
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

    def retrieve_json_from_id(self, solution_id):
        ids = self.read_file_with_ids()
        if solution_id in ids:
            with open(self.base_path_folders + solution_id + "/timetable.json", "r") as f:
                info = json.load(f)
                # After finding info from json, write to timetable.json
                with open("./test_assets/production/sim_json.json", "w") as o:
                    o.write(json.dumps(info, indent=4))
            with open(self.base_path_folders + solution_id + "/constraints.json", "r") as f:
                info = json.load(f)
                # After finding info from json, write to timetable.json
                with open("./test_assets/production/constraints.json", "w") as o:
                    o.write(json.dumps(info, indent=4))
                    return self.remove_id_from_list(solution_id)
        print("Err: Solution ID not found.")
