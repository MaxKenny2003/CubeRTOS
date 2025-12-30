import os
import json
import time

def create_folder():
    if os.path.exists("data/"):
        return
    else:
        os.mkdir("data")
    
    return

def create_file(file_name):
    file_path_and_name_temp = "data/" + file_name + "_temp.json"
    if os.path.exists(file_path_and_name_temp):
        os.remove(file_path_and_name_temp)

    f = open(file_path_and_name_temp, "x")

def write_to_json_temp_file(dataDict, file_name):
    file_path_and_name = "data/" + file_name + ".json"
    file_path_and_name_temp = "data/" + file_name + "_temp.json"
    dataDict["unix_time"] = time.time()
    y = json.dumps(dataDict)
    create_folder()
    create_file(file_name)
    with open(file_path_and_name_temp, "a") as f:
        f.write(y)
    os.replace(file_path_and_name_temp, file_path_and_name)
    