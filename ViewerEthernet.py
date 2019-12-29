'''
This code is for the receiver side for the Ethernet communication for the PC side.
The IP is for the PC. The same IP should be used in the sender side (in UP2 board).  
'''
import cv2
import zmq
import base64
import time
import numpy as np
context = zmq.Context()

# footage_socket = context.socket(zmq.SUB)
# # footage_socket.bind('tcp://192.168.183.215:5555')
# # footage_socket.bind('tcp://192.168.183.14:5555')
# footage_socket.bind("tcp://*:5555")
print("Connecting to hello world server…")
socket = context.socket(zmq.SUB)
socket.bind("tcp://*:5555")
socket.RCVTIMEO = 100

socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))
Camera = 1

DownSample = 2

cv2.namedWindow("Cam1", cv2.WINDOW_NORMAL)        # Create window with freedom of dimensions
# cv2.namedWindow("Cam2", cv2.WINDOW_NORMAL)        # Create window with freedom of dimensions
# cv2.namedWindow("Cam3", cv2.WINDOW_NORMAL)        # Create window with freedom of dimensions


while True:
    try:
        frame = socket.recv_string()
        #encoded, buffer = cv2.imencode('.jpg', frame)
        #jpg_as_text = base64.b64encode(buffer)
        img = base64.b64decode(frame)
        npimg = np.frombuffer(img, dtype=np.uint8)
        # source = cv2.imdecode(npimg, 1)

        print(npimg.shape)
        npimg = np.reshape(npimg, (750, 1000, 3))
        # npimg = np.reshape(npimg, (int(3000/DownSample), int(4000/DownSample), 3))
        source = cv2.cvtColor(npimg, cv2.COLOR_BGR2RGB)
        print(npimg.shape)

        cv2.imshow("Cam1", npimg)

        # if Camera == 1:
        #     cv2.imshow("Stream Camera 1", source)
        #     cv2.waitKey(1)
        #     Camera = 2
        # else:
        #     cv2.imshow("Stream Camera 2", source)
        #     cv2.waitKey(1)
        #     Camera = 1

    except:
        pass

    k = cv2.waitKey(33)
    if k == 27:  # wait for ESC key to exit
        cv2.destroyAllWindows()
        break