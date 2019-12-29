# import the necessary packages
# from imutils.video import FileVideoStream
# from video_stream import FileVideoStream

# import videostream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import cv2
import os
import PySpin
from FLIRCam.USB_video_stream import *
NUM_IMAGES = 3  # number of images to grab

import base64
import zmq
# context = zmq.Context()
# socket = context.socket(zmq.REP)
# socket.bind("tcp://*:5555")
context = zmq.Context()
socket = context.socket(zmq.PUB)
# socket.bind("tcp://*:5555")
socket.connect("tcp://localhost:5555")
# construct the argument parse and parse the arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-v", "--video", default='Big_Buck_Bunny_1080_10s_2MB.mp4',
# 	help="path to input video file")
# args = vars(ap.parse_args())

# start the file video stream thread and allow the buffer to start to fill

fvs = USBVideoStream() # .start()
fvs.start()
fps = FPS().start()

# loop over frames from the video file stream
while True:
    while not fvs.more():
        pass

    frame = fvs.read()

    image = imutils.resize(frame['image'], width=1000)
    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # frame = np.dstack([frame, frame, frame])


    # display the size of the queue on the frame
    cv2.putText(image, f"Queue Size: {fvs.Q.qsize()}, Camera {frame['cam']}",
        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    print(f"Queue Size: {fvs.Q.qsize()}, Camera {frame['cam']}, shape {image.shape}")
    # show the frame and update the FPS counter
    if frame['cam'] == 0:
        cv2.imshow("Cam0", image)
    else:
        cv2.imshow("Cam1", image)

    # encoded, buffer = cv2.imencode('.jpg', image)
    jpg_as_text = base64.b64encode(image)
    socket.send(jpg_as_text)


    fps.update()
    k = cv2.waitKey(100)
    if k == 27:  # Esc key to stop
        break
    elif k == -1:  # normally -1 returned,so don't print it
        continue
    else:
        print(k)


# do a bit of cleanup
fvs.stop()
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

cv2.destroyAllWindows()

del fvs