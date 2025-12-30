from picamera2 import Picamera2
import cv2
import numpy as np

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": "XRGB8888", "size": (640, 480)}))
picam2.start()

while True:
    frame = picam2.capture_array()
    img = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    kernel = np.array([[0, -1, 0],
                     [-1, 5, -1],
                     [0, -1, 0]])
    
    sharpened = cv2.filter2D(img, -1, kernel)


    cv2.imshow("Original", img)
    cv2.imshow("Sharpened", img)
    if cv2.waitKey(1) == ord('q'):
        break

cv2.destroyAllWindows()





# Just take a photo
# from picamera2 import Picamera2
# picam2 = Picamera2()
# picam2.start_and_capture_file("test.jpg")

# Just take video s
# from picamera2 import Picamera2
# picam2 = Picamera2()
# picam2.start_and_record_video("test.mp4", duration=5)
