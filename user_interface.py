import tkinter as tk
from PIL import Image, ImageFont, ImageDraw, ImageTk
import math
import cv2
import requests


class Window(tk.Tk):

    def __init__(self, video_stream, ai_manager, save_location):
        tk.Tk.__init__(self)
        # self.root.bind('<Escape>', lambda e: self.exit())

        container = tk.Frame(self)
        container.grid(row=0, column=0)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # for F in (CheckInScreen, GestureScreen):
        #     page_name = F.__name__
        #     frame = F(parent=container, controller=self)
        #     self.frames[page_name] = frame
        #
        #     frame.grid(row=0, column=0, sticky="nsew")

        self.frames["GestureScreen"] = GestureScreen(parent=container, controller=self, video_stream=video_stream,
                                                     ai_manager=ai_manager, save_location=save_location)
        self.frames["GestureScreen"].grid(row=0, column=0, sticky="nsew")
        self.frames["GestureScreen"].video_loop()
        self.frames["GestureScreen"].save_images()
        self.frames["CheckInScreen"] = GestureScreen(parent=container, controller=self)
        self.frames["CheckInScreen"].grid(row=0, column=0, sticky="nsew")

        self.show_frame("CheckInScreen")

        # self.root.wm_title("Supernova: Space invader")
        # self.root.wm_protocol("WM_DELETE_WINDOW", self.exit)
        # self.root.configure(background='#0e1c24')

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


class CustomFontLabel(tk.Label):
    def __init__(self, master, text, foreground="black", truetype_font=None, font_path=None, family=None, size=None,
                 **kwargs):
        if truetype_font is None:
            if font_path is None:
                raise ValueError("Font path can't be None")

            # Initialize font
            truetype_font = ImageFont.truetype(font_path, size)

        width, height = truetype_font.getsize(text)

        image = Image.new("RGBA", (width, height), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        draw.text((0, 0), text, font=truetype_font, fill=foreground)

        self._photoimage = ImageTk.PhotoImage(image)
        tk.Label.__init__(self, master, image=self._photoimage, **kwargs)


class CheckInScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        tk.Frame(bg="#0e1c24")

        welcome_lbl = CustomFontLabel(self,
                                      text="Welcome brave astronaut. Please enter your id to start "
                                           "your journey on this new planet.",
                                      font_path='resources/nidsans-webfont.ttf', size=22, bg='#51ffff', fg='#1b3848')
        welcome_lbl.grid(pady=10, ipadx=10)

        id_image = tk.PhotoImage(file="/home/craftworkz/Documents/SupernovaDemo/resources/astronaut.png")
        id_lbl = tk.Label(self, image=id_image)
        id_lbl.image = id_lbl
        id_lbl.grid(row=1, pady=10)


class GestureScreen(tk.Frame):
    FONT = cv2.FONT_HERSHEY_SIMPLEX

    training = False
    gesture = None
    wait_time = 30
    classifying = False

    def __init__(self, parent, controller, video_stream, ai_manager, save_location):
        self.ai_manager = ai_manager
        self.video_stream = video_stream
        self.save_location = save_location

        tk.Frame.__init__(self, parent)
        self.controller = controller

        # background
        background_image = tk.PhotoImage(file="/home/craftworkz/Documents/SupernovaDemo/resources/bg.png")
        background_lbl = tk.Label(self, image=background_image)
        background_lbl.image = background_image
        background_lbl.place(x=0, y=0, relwidth=1, relheight=1)

        # craftworkz logo
        logo = tk.PhotoImage(
            file="/home/craftworkz/Documents/SupernovaDemo/resources/craftworkz_icon75.png")
        logo_lbl = tk.Label(self, image=logo)
        logo_lbl.image = logo
        logo_lbl.grid(row=10, column=2, rowspan=3, padx=5, pady=5, sticky=tk.E)

        self.panel = None
        label = CustomFontLabel(self, text="Click the buttons to start and stop recording gestures.",
                                font_path='resources/nidsans-webfont.ttf', size=22, bg='#51ffff', fg='#1b3848')
        label.grid(row=0, columnspan=4, padx=10, pady=5, ipady=2.5, ipadx=5)

        # label and buttons to go left
        lbl = CustomFontLabel(self, text="Gestures to go left", font_path='resources/nidsans-webfont.ttf', size=16,
                              bg='#95cc71', fg='#1b3848', width=250)
        lbl.grid(row=1, column=1, columnspan=2, padx=5, sticky=tk.W, ipady=2.5)

        btn = tk.Button(self, text="Train!", command=lambda: self.start_clicked('left'), width=5,
                        highlightthickness=0, bd=0)
        btn.grid(row=2, column=1)

        btn = tk.Button(self, text="Reset!", command=lambda: self.reset_clicked('space'), width=5,
                        highlightthickness=0, bd=0)
        btn.grid(row=2, column=2)

        # label and buttons to go right
        lbl = CustomFontLabel(self, text="Gestures to go right", font_path='resources/nidsans-webfont.ttf',
                              size=16,
                              bg='#95cc71', fg='#1b3848', width=250)
        lbl.grid(row=3, column=1, columnspan=2, padx=5, sticky=tk.W, ipady=2.5)

        btn = tk.Button(self, text="Train!", command=lambda: self.start_clicked('right'), width=5,
                        highlightthickness=0, bd=0)
        btn.grid(row=4, column=1)

        btn = tk.Button(self, text="Reset!", command=lambda: self.reset_clicked('space'), width=5,
                        highlightthickness=0, bd=0)
        btn.grid(row=4, column=2)

        # label and buttons to shoot
        lbl = CustomFontLabel(self, text="Gestures to shoot", font_path='resources/nidsans-webfont.ttf', size=16,
                              bg='#95cc71', fg='#1b3848', width=250)
        lbl.grid(row=5, column=1, columnspan=2, padx=5, sticky=tk.W, ipady=2.5)

        btn = tk.Button(self, text="Start!", command=lambda: self.start_clicked('space'), width=5,
                        highlightthickness=0, bd=0)
        btn.grid(row=6, column=1)

        btn = tk.Button(self, text="Reset!", command=lambda: self.reset_clicked('space'), width=5,
                        highlightthickness=0, bd=0)
        btn.grid(row=6, column=2)

        # id
        lbl = CustomFontLabel(self, text="id: ", font_path='resources/nidsans-webfont.ttf', size=16,
                              fg='#ffffff', bg="#51ffff")
        lbl.grid(row=10, column=0, sticky=tk.W, padx=10, rowspan=3, pady=10)
        self.txt = tk.Text(self, height=1, width=10)
        self.txt.grid(row=10, column=0, sticky=tk.W, padx=50, rowspan=3, pady=10)

        # space invader
        btn = tk.Button(self, text="Start space invader", command=self.start_space_invaders, width=50,
                        height=2, highlightthickness=0, bd=0, bg="#51ffff")
        btn.grid(row=10, column=0, columnspan=3, rowspan=3, pady=10)

    def video_loop(self):
        try:
            frame = self.video_stream.frame
            # image = self.convert(self.video_stream.frame)
            if not self.ai_manager.training:
                if self.classifying:
                    prediction, probability = self.ai_manager.classify_gesture_on_image(self.video_stream.frame)
                    frame = cv2.putText(frame, 'Predicted gesture: {}'.format(prediction), (5, 15),
                                        self.FONT,
                                        0.5, (255, 255, 255), 1, cv2.LINE_AA)
                image = self.convert(frame)
            else:
                if self.wait_time == 0:
                    height, width, _ = frame.shape
                    frame = cv2.putText(frame, 'Training', (20, 25),
                                        self.FONT,
                                        0.5, (255, 255, 255), 1, cv2.LINE_AA)
                    """frame = cv2.rectangle(frame, (int((width / 2) - 202), 8), (int((width / 2) + 202), 32),
                                          (72, 56, 27), 2)"""
                    frame = cv2.rectangle(frame, (int((width / 2) - 202), 8), (int((width / 2) + 202), 32),
                                          (255, 255, 255), 2)
                    frame = cv2.rectangle(frame, (int((width / 2) - 200), 10),
                                          (int((width / 2) + (
                                                  (8 * (len(self.ai_manager.train_dict.get(self.gesture)) + 1)) - 200)),
                                           30),
                                          (169, 151, 58),
                                          cv2.FILLED)
                else:
                    text = str(math.ceil(self.wait_time / 10))
                    text_size = cv2.getTextSize(text, self.FONT, 5, 5)[0]
                    text_x = (frame.shape[1] - text_size[0]) // 2
                    text_y = (frame.shape[0] + text_size[1]) // 2
                    frame = cv2.putText(frame, text, (text_x, text_y), self.FONT, 5, (255, 255, 255), 5)
                image = self.convert(frame)

            if self.panel is None:
                self.panel = tk.Label(image=image)
                self.panel.image = image
                self.panel.grid(row=1, rowspan=6, padx=10, pady=10)
            else:
                self.panel.configure(image=image)
                self.panel.image = image
        except RuntimeError as e:
            print("[INFO] caught a RuntimeError!")
            print(e)

        self.after(40, self.video_loop)

    def save_images(self):
        if self.ai_manager.training:
            if self.wait_time == 0:
                curr_frame_features = self.ai_manager.inception.get_features_from_image(self.video_stream.frame)
                self.ai_manager.train_dict.get(self.gesture).append(curr_frame_features)
                if len(self.ai_manager.train_dict.get(self.gesture)) >= 50:
                    self.stop_save()
            else:
                self.wait_time -= 1
        self.after(100, self.save_images)

    def convert(self, img):
        img = cv2.resize(img, (640, 480))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img = ImageTk.PhotoImage(img)
        return img

    def start_clicked(self, gesture):
        if not self.ai_manager.training:
            self.gesture = gesture
            self.ai_manager.train_dict.get(gesture).clear()
            self.ai_manager.training = True

    def reset_clicked(self, gesture):
        self.ai_manager.train_dict.get(gesture).clear()
        features, classes = self.ai_manager.get_features_and_classes_from_dict(self.ai_manager.train_dict)
        self.ai_manager.knn.train_new_knn_classifier(features, classes)
        self.ai_manager.training = False

    def stop_save(self):
        features, classes = self.ai_manager.get_features_and_classes_from_dict(self.ai_manager.train_dict)
        self.ai_manager.knn.train_new_knn_classifier(features, classes)
        self.ai_manager.training = False
        self.wait_time = 30

    def exit(self):
        self.video_stream.stop()
        self.quit()
        exit(0)

    def start_space_invaders(self):
        if len(self.txt.get("1.0", tk.END)) == 1:
            lbl = CustomFontLabel(self, text="You need to fill in your id! ",
                                  font_path='resources/nidsans-webfont.ttf', size=16,
                                  fg='#ffffff', bg="#ef5332")
            lbl.grid(column=0, row=9, columnspan=3)
        else:
            response = requests.get("http://supernova.madebyartcore.com/api/checkin/[company_id]/[astronaut_id]")
            data = response.json()
            # data["firstname"]

            response = requests.post(
                "http://supernova.madebyartcore.com/api/checkout/[points]/[company_id]/[astronaut_id]")
            if not self.classifying:
                self.classifying = True
            else:
                self.classifying = False
