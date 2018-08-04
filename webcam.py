import threading
import cv2


class WebcamStream:
    def __init__(self, src):
        self.stream = cv2.VideoCapture(src)

        (self.ret, self.frame) = self.stream.read()
        self.stopped = False

    def start(self):
        threading.Thread(target=self.update, args=()).start()
        return self

    def update(self):
        while True:
            if self.stopped:
                return

            (self.ret, self.frame) = self.stream.read()

    def read(self):
        return self.ret, self.frame

    def stop(self):
        self.stopped = True
