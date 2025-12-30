import os
import json
import csv
from pathlib import Path
import time

log_file_path = Path("logs")

def retrieve_latest_log_file():
    if not os.path.exists(log_file_path):
        os.mkdir(log_file_path)

    log_files = sorted(
            [f for f in log_file_path.glob(f"{"log"}_*.txt")],
            key=lambda p: int(p.stem.split("_")[-1]) if "_" in p.stem else 0
        )
    
    if not log_files:
        target_file = "logs/log_0.txt"
        Path(target_file).touch()
        file_created_log(target_file)
    else:
        newest_file = log_files[-1]
        with newest_file.open(newline="", encoding="utf-8") as textFile:
            line_count = sum(1 for _ in textFile)

        if line_count > 1000:
            new_file_suffix = len(log_files)
            target_file = "logs/" + f"log_{new_file_suffix}.txt"
            Path(target_file).touch()
            file_created_log(target_file)
        else:
            target_file = newest_file

    return target_file

def file_created_log(file_name):
    # Encode to bytes for os.write()
    target_file = retrieve_latest_log_file()
    path = target_file
    text = f"Created file: {file_name} at {time.time()}\r\n"
    data = text.encode("utf-8")

    # Open file with O_APPEND so kernel appends atomically
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND)

    try:
        os.write(fd, data)  # atomic append
        os.fsync(fd)        # ensure data hits disk
    finally:
        os.close(fd)

def gps_lock_aquired_log():
    target_file = retrieve_latest_log_file()
    path = target_file
    text = f"GPS: Lock Aquired at {time.time()}\r\n"
    data = text.encode("utf-8")

    # Open file with O_APPEND so kernel appends atomically
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND)

    try:
        os.write(fd, data)  # atomic append
        os.fsync(fd)        # ensure data hits disk
    finally:
        os.close(fd)

def picture_log(picture_name):
    target_file = retrieve_latest_log_file()
    path = target_file
    text = f"GPS: Picture: {picture_name} taken at {time.time()}\r\n"
    data = text.encode("utf-8")

    # Open file with O_APPEND so kernel appends atomically
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND)

    try:
        os.write(fd, data)  # atomic append
        os.fsync(fd)        # ensure data hits disk
    finally:
        os.close(fd)