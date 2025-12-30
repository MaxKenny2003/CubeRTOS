import os
import json
import csv
from pathlib import Path
import logging_events_helper


def write_data(files_to_read, data_name):
    files_read = 0
    
    raw_data_folder_path = "data"
    no_file = False

    running_data_file = data_name + "_running_data.json"

    # Load in main running data
    with open("main_running_data.json", "r") as f:
        main_data = json.load(f)

    file_path = Path(running_data_file)
    if not file_path.exists() or file_path.stat().st_size == 0:
        with open(running_data_file, "w") as f:
            json.dump({}, f, indent=4)

    with open(running_data_file, "r") as f:
        running_data = json.load(f)

    # Read and merge data into the main json file for ease of data access
    for filename in files_to_read:
        file_path = os.path.join(raw_data_folder_path, filename)

        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
                main_data.update(data)
                running_data.update(data)
            os.remove(file_path)
            files_read += 1

    # Write changes back to disk
    with open("main_running_data.json", "w") as f:
        json.dump(main_data, f, indent=4)
    with open(running_data_file, "w") as f:
        json.dump(running_data, f, indent=4)


    ### Here is where the CSV stuff is written
    if files_read > 0:
        # Check to see if the folder for this data exists
        csv_path_name = data_name
        # Ensure folder exists
        csv_folder_path = Path(csv_path_name)
        csv_folder_path.mkdir(exist_ok=True)

        # Find all CSV files in that folder
        csv_files = sorted(
            [f for f in csv_folder_path.glob(f"{data_name}_*.csv")],
            key=lambda p: int(p.stem.split("_")[-1]) if "_" in p.stem else 0
        )

        # Determine target file
        if not csv_files:
            # Start fresh with _0.csv
            target_file = csv_folder_path / f"{data_name}_0.csv"
            logging_events_helper.file_created_log(f"{data_name}_0.csv")
        else:
            newest_file = csv_files[-1]
            with newest_file.open(newline="", encoding="utf-8") as csvfile:
                row_count = sum(1 for _ in csv.reader(csvfile))

            # If file has >10 rows, start a new one
            if row_count > 1000:
                new_file_suffix = len(csv_files)
                target_file = csv_folder_path / f"{data_name}_{new_file_suffix}.csv"
                logging_events_helper.file_created_log(f"{data_name}_{new_file_suffix}.csv")
            else:
                target_file = newest_file

        # Write data
        file_exists = target_file.exists() and target_file.stat().st_size > 0

        with target_file.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=running_data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(running_data)
