# import the necessary packages
from threading import Thread
import sys
import time
import PySpin

# import the Queue class from Python 3
if sys.version_info >= (3, 0):
    from queue import Queue

# otherwise, import the Queue class for Python 2.7
else:
    from Queue import Queue


class FileVideoStream:
    def __init__(self, transform=None, queue_size=10):
        # initialize the file video stream along with the boolean
        # used to indicate if the thread should be stopped or not
        self.stopped = False
        self.transform = transform

        # initialize the queue used to store frames read from the video file
        self.Q = Queue(maxsize=queue_size)
        # intialize thread
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True

        self.system = PySpin.System.GetInstance()  # Retrieve singleton reference to system object
        version = self.system.GetLibraryVersion()  # Get current library version
        print('Library version: %d.%d.%d.%d' % (version.major, version.minor, version.type, version.build))

        self.camlist = self.system.GetCameras()  # Retrieve list of cameras from the system

        # num_cameras =
        # for cam in cam_list: cam.DeInit()
        # system.ReleaseInstance()

        print(f'Number of cameras detected: {self.camlist.GetSize()}')

    def __del__(self):
        self.camlist.Clear()
        self.system.ReleaseInstance()

    def set_cam_mode_continuous(self, i, cam):
        node_acquisition_mode = PySpin.CEnumerationPtr(cam.GetNodeMap().GetNode('AcquisitionMode'))
        if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
            print('Unable to set acquisition mode to continuous . Aborting... \n')
            return False

        node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
        if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(
                node_acquisition_mode_continuous):
            print('Unable to set acquisition mode to continuous , Aborting... \n')
            return False

        acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()
        node_acquisition_mode.SetIntValue(acquisition_mode_continuous)
        print('Camera acquisition mode set to continuous...')
        return True

    def start(self):
        for i, cam in enumerate(self.camlist): cam.Init()  # intialize cameras

        for i, cam in enumerate(self.camlist):

            # Set acquisition mode to continuous
            self.set_cam_mode_continuous(i, cam)

            # Begin acquiring images
            cam.BeginAcquisition()

            print('Camera %d started acquiring images...' % i)
            print()
        # start a thread to read frames from the file video stream
        self.thread.start()
        return self

    def update(self):
        # keep looping infinitely
        while True:
            # if the thread indicator variable is set, stop the
            # thread
            if self.stopped:
                break

            # otherwise, ensure the queue has room in it
            if not self.Q.full():
                for i, cam in enumerate(self.camlist):
                    try:
                        frame = cam.GetNextImage()
                        image_converted = frame.Convert(PySpin.PixelFormat_Mono8, PySpin.HQ_LINEAR)
                        image_converted = image_converted.GetNDArray()
                        print(f'Image retrieved from cam {i}, shape = {image_converted.shape}')
                        frame.Release()  # Release image
                        # producer/consumer queues since this one was generally
                        # idle grabbing frames.
                        if self.transform:
                            image_converted = self.transform(image_converted)

                        # add the frame to the queue
                        self.Q.put({'cam':i, 'image':image_converted})

                    except PySpin.SpinnakerException as ex:
                        print('Error: %s' % ex)
                        self.stopped = True

            else:
                time.sleep(0.1)  # Rest for 10ms, we have a full queue

        # self.stream.release()
        for cam in self.camlist:
            # End acquisition
            cam.EndAcquisition()
            cam.DeInit()

    def read(self):
        # return next frame in the queue
        return self.Q.get()

    # Insufficient to have consumer use while(more()) which does
    # not take into account if the producer has reached end of
    # file stream.
    def running(self):
        return self.more() or not self.stopped

    def more(self):
        # return True if there are still frames in the queue. If stream is not stopped, try to wait a moment
        tries = 0
        while self.Q.qsize() == 0 and not self.stopped and tries < 5:
            time.sleep(0.1)
            tries += 1

        return self.Q.qsize() > 1

    def queue_size(self):
        return self.Q.qsize()

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
        # wait until stream resources are released (producer thread might be still grabbing frame)
        self.thread.join()
