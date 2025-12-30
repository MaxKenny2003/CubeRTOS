import os
import time
import json
import read_helpers
import sys

def main():
    #print("test1 :0")

    ### Test writing of file ###
    # x = {"temp" : 1, "temp2" : 3, "temp3" : 6}

    # # if os.path.exists("data/test.json"):
    # #     os.remove("data/test.json")
    # # with open("data/test.json", "a") as f:
    # #     f.write(json.dumps(x))
    # #     f.write("\r\n")
    # read_helpers.create_folder()
    # read_helpers.create_file("testFile")
    # read_helpers.write_to_json_temp_file(x, "testFile")

    ### Test erroring ### 
    print("Test1 :0")
    sys.exit(1)
    
if __name__  == "__main__":
    main()