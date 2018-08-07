from tkinter import *
from PIL import Image, ImageTk
import time
import cv2


class Window:
    training = False
    retrain = False
    gesture = None
    index = 0

    def __init__(self, video_stream, ai_manager, save_location):
        self.ai_manager = ai_manager
        self.vs = video_stream

        self.save_location = save_location

        self.root = Tk()
        self.root.bind('<Escape>', lambda e: self.stop())
        self.panel = None
        self.label = Label(self.root, text="Click the buttons to start and stop recording gestures.")
        self.label.grid(row=0, columnspan=4)
        lbl = Label(self.root, text="Gestures to go left")
        lbl.grid(row=1, column=1, columnspan=2)
        btn = Button(self.root, text="Start!", command=lambda: self.start_clicked('left'))
        btn.grid(row=2, column=1, padx=10)
        btn = Button(self.root, text="Stop!", command=self.stop_clicked)
        btn.grid(row=2, column=2, padx=10)
        lbl = Label(self.root, text="Gestures to go right")
        lbl.grid(row=3, column=1, columnspan=2)
        btn = Button(self.root, text="Start!", command=lambda: self.start_clicked('right'))
        btn.grid(row=4, column=1, padx=10, pady=10)
        btn = Button(self.root, text="Stop!", command=self.stop_clicked)
        btn.grid(row=4, column=2, padx=10, pady=10)
        lbl = Label(self.root, text="Gestures to shoot")
        lbl.grid(row=5, column=1, columnspan=2)
        btn = Button(self.root, text="Start!", command=lambda: self.start_clicked('space'))
        btn.grid(row=6, column=1, padx=10, pady=10)
        btn = Button(self.root, text="Stop!", command=self.stop_clicked)
        btn.grid(row=6, column=2)
        self.root.wm_title("Supernova: Space invader")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.stop)

    def video_loop(self):
        try:
            image = self.convert(self.vs.frame)
            if not self.ai_manager.training:
                prediction, _ = self.ai_manager.classify_gesture_on_image(image)
                image = cv2.putText(image, 'Predicted gesture: {}'.format(prediction), (5, 5), cv2.FONT_HERSHEY_SIMPLEX,
                                    0.5, (0, 255, 0), 1, cv2.LINE_AA)

            if self.panel is None:
                self.panel = Label(image=image)
                self.panel.image = image
                self.panel.grid(row=1, rowspan=6, padx=10, pady=10)
            else:
                self.panel.configure(image=image)
                self.panel.image = image
        except RuntimeError as e:
            print("[INFO] caught a RuntimeError!")

        self.root.after(16, self.video_loop)

    def save_images(self):
        if self.ai_manager.training:
            cv2.imwrite('{}/{}/{}.jpg'.format(self.save_location, self.gesture, self.index))
            self.index += 1
        self.root.after(100, self.save_images)

    def convert(self, img):
        img = cv2.resize(img, (640, 480))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img = ImageTk.PhotoImage(img)
        return img

    def start_clicked(self, gesture):
        time.sleep(3)
        self.ai_manager.training = True
        self.gesture = gesture

    def stop_clicked(self):
        dict = self.ai_manager.load_images_into_dict(self.save_location)
        features, classes = self.ai_manager.get_features_and_classes_from_dict(dict)
        self.ai_manager.knn.train_new_knn_classifier(features, classes)
        self.ai_manager.training = False

    def stop(self):
        self.vs.stop()
        self.root.quit()
        exit(0)
