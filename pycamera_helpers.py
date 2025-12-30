import cv2
import numpy as np
import glob
from pathlib import Path
import base64
import json
import encode
import struct
import os
import math
import re

### Below are the functions for image modifying and changing ### 

def pick_best_image(img_path):
    cv_img = cv2.imread(img_path)

    if cv_img is None:
        raise ValueError(f"Could not read image: {img_path}")

    # Downscale massively for speed
    cv_img = cv2.resize(cv_img, (160, 120))   # 160x120 = 0.2% of original pixels
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

    score = horizon_focus_score(gray)
    print(f"{img_path}: {score:.2f}")

    return score


def sharpness(image):
    #gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(image, cv2.CV_64F).var()

def horizon_strength(image):
    #gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = image
    edges = cv2.Canny(gray, 50, 150)

    # Use Sobel to find gradients
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    
    # Magnitude of horizontal edges (change along y-axis)
    horizontal_strength = np.mean(np.abs(sobely))
    vertical_strength = np.mean(np.abs(sobelx))
    
    # Horizon lines → stronger horizontal edges than vertical ones
    if vertical_strength == 0:
        return 0
    return horizontal_strength / (vertical_strength + 1e-6)

def horizon_focus_score(image):
    s = sharpness(image)
    h = horizon_strength(image)
    return s * h

# Need a way to know what the file number is
def split_image_to_chunks(image_path, pid, command_image_name, packet_size=225, output_folder="decomposed"):
    """
    Splits an image into 225-byte chunks and stores them in a JSON file.
    Each chunk is base64-encoded for safe storage in JSON.
    """
    # image_path = Path(image_path) # Already is a path
    output_folder = Path(output_folder)
    output_folder.mkdir(exist_ok=True)

    # Output JSON file: decomposed/<image_name>.json
    command_image_name = Path(command_image_name)
    json_path = output_folder / f"{command_image_name.stem}.json"

    # Read image as raw bytes
    with open(image_path, "rb") as f:
        data = f.read()
    
    data_len = len(data)
    packet_size = 225

    match = re.search(r"(\d+)", command_image_name.stem)
    if not match:
        raise ValueError(f"No number found in image name: {command_image_name}")

    file_number = int(match.group(1))

    num_chunks = math.ceil(data_len / packet_size)
    packets = {}
    part_num = 0
    for i in range(0, len(data), packet_size):
        chunk = data[i:i+packet_size]
        chunk_size = len(chunk)

        # Build DAP packet for this chunk
        dap = dap_packet_chunk(chunk, pid, num_chunks, file_number, part_num)

        # Wrap DAP inside RAP packet
        rap = encode.encode_rap(0x01, dap)

        # Store BASE64(RAP) in the JSON
        encoded = base64.b64encode(rap).decode("ascii")

        packets[str(i // packet_size)] = encoded
        part_num += 1

    # Save JSON
    with open(json_path, "w") as f:
        json.dump(packets, f, indent=4)

    print(f"Image split into {len(packets)} packets → saved to {json_path}")
    


### Below are the functions for creating beacons ### 
def decode_cap(cap_bytes):
    """
    Decode CAP packet from RAP.DATA.
    Returns (pid, ref_num, cmd, args)
    """

    if len(cap_bytes) < 6:
        raise ValueError("CAP packet too short")

    pid      = cap_bytes[0]
    length   = int.from_bytes(cap_bytes[1:3], "little")      # data length (ignored)
    ref_num  = int.from_bytes(cap_bytes[3:5],"little")
    exe_time = int.from_bytes(cap_bytes[5:9], "little")
    # exe_time = cap_bytes[3]    # ignored
    cmd_bytes = cap_bytes[9:11]
    args_bytes = cap_bytes[11:-2]
    # Decode safely as ASCII (commands are ASCII per ICD)
    args = args_bytes.decode("ascii")
    cmd = int.from_bytes(cmd_bytes)

    return pid, ref_num, cmd, args


def send_ack(pid, ref, cmd):
    data = bytearray()
    data += pid.to_bytes(1, "little")
    data += cmd.to_bytes(2, "little")
    data += ref.to_bytes(2, "little")

    rap = encode.encode_rap(0x05, data)

    # Base64 encode for safe text storage
    encoded = base64.b64encode(rap).decode("ascii")

    os.makedirs("transmission_data", exist_ok=True)
    with open("transmission_data/data", "a") as f:
        f.write(encoded + "\n")

def create_transmit_doc_all(image_name):
    image_name = Path(image_name)
    filepath = f"decomposed/{image_name.stem}.json"

    # Suppose your JSON is in a file called 'data.json'
    with open(filepath, "r") as f:
        data = json.load(f)

    os.makedirs("transmission_data", exist_ok=True)

    # Open a text file to write all values
    with open("transmission_data/data", "a") as f:
        for key in sorted(data.keys(), key=int):  # sort keys numerically
            f.write(data[key] + "\n")  # add a newline after each value

    print("Finished writing")
    
def create_transmit_doc_partial(image_name,args):
    image_name = Path(image_name)
    filepath = f"decomposed/{image_name.stem}.json"
    with open(filepath, "r") as f:
        data = json.load(f)

    # Ensure output directory exists
    os.makedirs("transmission_data", exist_ok=True)

    # Write selected values to a file
    with open("transmission_data/data", "a") as f:
        for key in args:
            if key in data:
                f.write(data[key] + "\n")
    
    print("Finished this")

def dap_packet_chunk(chunk, pid, num_chunks, file_number, file_part):
    data = bytearray()
    pid_bytes = pid.to_bytes(1, "little")
    length = len(chunk) + 9
    length_bytes = length.to_bytes(2, "little")
    file_number_bytes = file_number.to_bytes(2,"little")
    file_part_bytes = file_part.to_bytes(2,"little")
    total_parts_bytes = num_chunks.to_bytes(2, "little")

    data += pid_bytes
    data += length_bytes
    data += file_number_bytes
    data += file_part_bytes
    data += total_parts_bytes
    data += chunk

    return data

