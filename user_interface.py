from tkinter import *
from PIL import Image, ImageTk
import time
import cv2


# Here, we are creating our class, Window, and inheriting from the Frame

# class. Frame is a class from the tkinter module. (see Lib/tkinter/__init__)
class Window:
    training = False
    retrain = False
    gesture = None

    # Define settings upon initialization. Here you can specify
    def __init__(self, vs):
        # Store the video stream object and initialize the most recent frame
        # Thread for reading frames with the stop event
        self.vs = vs
        self.frame = None
        self.thread = None
        self.stop_event = None
        # Initialise the root window and the panel for the video stream
        self.root = Tk()
        self.root.bind('<Escape>', lambda e: self.stop())
        self.panel = None
        # Create a label in which we can display text to the user
        self.label = Label(self.root, text="Click the buttons to start and stop recording gestures.")
        self.label.grid(row=0, columnspan=4)
        # Create two buttons. One with the text start to start the game
        # and one with reset to clear the points so that you can chose them again
        # label and buttons to go left
        lbl = Label(self.root, text="Gestures to go left")
        lbl.grid(row=1, column=1, columnspan=2)
        btn = Button(self.root, text="Start!", command=lambda: self.start_clicked('left'))
        btn.grid(row=2, column=1, padx=10)
        btn = Button(self.root, text="Stop!", command=self.stop_clicked)
        btn.grid(row=2, column=2, padx=10)
        # label and buttons to go right
        lbl = Label(self.root, text="Gestures to go right")
        lbl.grid(row=3, column=1, columnspan=2)
        btn = Button(self.root, text="Start!", command=lambda: self.start_clicked('right'))
        btn.grid(row=4, column=1, padx=10, pady=10)
        btn = Button(self.root, text="Stop!", command=self.stop_clicked)
        btn.grid(row=4, column=2, padx=10, pady=10)
        # label and buttons to shoot
        lbl = Label(self.root, text="Gestures to shoot")
        lbl.grid(row=5, column=1, columnspan=2)
        btn = Button(self.root, text="Start!", command=lambda: self.start_clicked('space'))
        btn.grid(row=6, column=1, padx=10, pady=10)
        btn = Button(self.root, text="Stop!", command=self.stop_clicked)
        btn.grid(row=6, column=2)
        # Start a thread that will get the most recent frame from the video sensor
        """self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.video_loop, args=())
        self.thread.start()"""
        # Set a title on the window and set a callback to handle when the window is closed
        self.root.wm_title("Supernova: Space invader")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.on_close)

    def video_loop(self):
        # Tkinter is know to have problems with threading. To avoid problems we use this try/except statement
        # to work around that problem
        try:
            # Keep looping over the frames until the thread is instructed to stop
            #  Get the image from the camera and resize it to a maximum with of 300px
            self.frame = self.vs.frame
            image = self.convert(self.frame)
            # If the panel is None we need to initialise it
            # We also bind that if the user clicks on the panel it will trigger the mouse_clicked function
            if self.panel is None:
                self.panel = Label(image=image)
                self.panel.image = image
                # self.panel.bind("<Button-1>", self.mouse_clicked)
                self.panel.grid(row=1, rowspan=6, padx=10, pady=10)
            # Otherwise just update the panel.
            else:
                self.panel.configure(image=image)
                self.panel.image = image
        except RuntimeError as e:
            print("[INFO] caught a RuntimeError!")

        self.root.after(1, self.video_loop)

    def convert(self, img):
        img = cv2.resize(img, (640, 480))
        # First convert the OpenCV (BGR) color order to the one PIL (RGB) needs
        # Next convert the image to a PIL and ImageTk format
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img = ImageTk.PhotoImage(img)
        return img

    def start_clicked(self, gesture):
        time.sleep(3)
        self.training = True
        self.gesture = gesture

    def stop_clicked(self):
        self.training = False
        self.retrain = True

    def on_close(self):
        # When the window is closed stop the threads, video stream and window
        print("[INFO] closing..")
        self.stop_event.set()
        self.vs.stop()
        self.root.quit()

    def stop(self):
        self.vs.stop()
        self.root.quit()
        exit(0)
