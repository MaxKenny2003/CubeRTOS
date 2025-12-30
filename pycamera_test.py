import board
import busio
import digitalio
import adafruit_rfm9x
import decode
import pycamera_helpers
from pathlib import Path
import glob
import base64
import struct

# Information already recieved 
pid = 10
ref = 5
cmd = "HeHe"
args = ["1", "4", "0", "6", "8", "7"]


best_score = -1
best_image = ""
pycamera_helpers.send_ack(pid, ref, cmd)        # send the ack
# Output of glob is a list of strings
for string_file_path in glob.glob(f"Images/*.jpg"):  
        # Load the image
        current_image_score = pycamera_helpers.pick_best_image(string_file_path)    # Here we are passing in a string (Images/Image0.jpg)
        if current_image_score > best_score:
            best_score = current_image_score
            best_image = string_file_path   # best image will be a string that has Images/name.jpg


    

if string_file_path is None:
    raise ValueError("No image found in Images/ folder")

# Get just the stem (filename without folder or extension)
name = Path(string_file_path).stem  # Should just be a sstring without the .jpg

# Call your decomposition function
pycamera_helpers.split_image_to_chunks(string_file_path, pid, best_image)

#pycamera_helpers.create_transmit_doc_all(name)
pycamera_helpers.create_transmit_doc_all(name)


