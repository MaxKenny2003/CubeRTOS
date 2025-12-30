import board
import busio
import digitalio
import adafruit_rfm9x
import decode
import pycamera_helpers
from pathlib import Path
import shutil
import glob
import base64
import struct
from encode import encode_rap
from digitalio import DigitalInOut, Direction, Pull
import decode
import os

CS = DigitalInOut(board.CE1) # init CS pin for SPI
RESET = DigitalInOut(board.D25) # init RESET pin for the RFM9x module
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO) # init SPI
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 436.95) # init object for the radio

best_score = -1

packet = rfm9x.receive()
if packet is not None:
    if not os.path.isfile("transmission_data/data") or os.path.getsize("transmission_data/data") == 0:
    
        print("Received:", packet)
        packet, rap, pid, sid, rap_type = decode.decode_rap(packet)

        pid, ref, cmd, args = pycamera_helpers.decode_cap(rap)
        
        # We should now have a decoded command. 
        values = [v.strip() for v in args.split(",")]      # Split packet by the , and remove any spaces from the values
        
        for i in values:
            print(i)
        
        if values[0].startswith("ImageFile") and values[1] == "ALL":
            print("Sending all")
            image_file_name = values[0]
            pycamera_helpers.send_ack(pid, ref, cmd)
            for string_file_path in glob.glob(f"Images/*.jpg"):  
                # Load the image
                current_image_score = pycamera_helpers.pick_best_image(string_file_path)    # Here we are passing in a string (Images/Image0.jpg)
                if current_image_score > best_score:
                    best_score = current_image_score
                    best_image = string_file_path   # best image will be a string that has Images/name.jpg
            

            name = Path(best_image)     # Should return just the image 
            pycamera_helpers.split_image_to_chunks(name, pid, image_file_name)
            pycamera_helpers.create_transmit_doc_all(image_file_name)
            source = "Images/"
            destination = Path("ImagesSent/")
            destination.mkdir(exist_ok=True)
            for file_path in glob.glob(source + "*"):
                shutil.move(file_path, destination)
            best_score = -1
        else:
            print("Sending partial")
            name = values[0]
            # We are requesting parts
            pycamera_helpers.send_ack(pid, ref, cmd)

            pycamera_helpers.create_transmit_doc_partial(values[0], values)
    
    



