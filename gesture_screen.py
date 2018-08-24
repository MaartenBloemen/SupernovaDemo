from tkinter import *
import tkinter.font as tkFont
from PIL import Image, ImageFont, ImageDraw, ImageTk
from spaceinvaders_simple import SpaceInvaders
import math
import cv2
import requests


class Window:
    FONT = cv2.FONT_HERSHEY_SIMPLEX

    training = False
    gesture = None
    wait_time = 30

    def __init__(self, video_stream, ai_manager, save_location):
        self.ai_manager = ai_manager
        self.video_stream = video_stream
        self.save_location = save_location

        self.resolution = 1.76666
        self.company_id = 0
        self.last_score = -1
        self.last_id = 0
        self.last_name = "John"
        self.ranking = {'-1': -1, '-2': -1, '-3': -1, '-4': -1, '-5': -1}
        self.name_list = {'-1': 'John', '-2': 'Jane', '-3': 'Jo', '-4': 'Jean', '-5': 'Jonas'}

        self.root = Tk()
        self.root.attributes("-fullscreen", True)
        self.root.bind('<Escape>', lambda e: self.exit())
        self.font = tkFont.Font(family='monospace', size=20, weight='bold')

        # background
        background_image = PhotoImage(file="/home/craftworkz/Documents/SupernovaDemo/resources/header1.png")
        background_label = Label(self.root, image=background_image)
        background_label.image = background_image
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        # craftworkz logo
        logo = PhotoImage(
            file="/home/craftworkz/Documents/SupernovaDemo/resources/craftworkz.png")
        logo_lbl = Label(self.root, image=logo)
        logo_lbl.image = logo
        logo_lbl.grid(row=10, column=3, rowspan=3, padx=5, pady=5)

        self.panel = None
        label = CustomFontLabel(self.root, text="Click the buttons to start and stop recording gestures.",
                                font_path='resources/nidsans-webfont.ttf', size=30, bg='#51ffff',
                                fg='#1b3848', width=int(825 * self.resolution))
        label.grid(row=0, columnspan=3, padx=10, pady=5, ipady=2.5, ipadx=5)

        # label and buttons to go left
        lbl = CustomFontLabel(self.root, text="Gestures to go left", font_path='resources/nidsans-webfont.ttf',
                              bg='#95cc71', fg='#1b3848', width=int(250 * self.resolution))
        lbl.grid(row=1, column=1, columnspan=2, padx=5, sticky=W, ipady=2.5)

        btn = Button(self.root, text="Train!", command=lambda: self.start_clicked('left'),
                     width=int(5 * self.resolution), font=self.font,
                     highlightthickness=0, bd=0)
        btn.grid(row=2, column=1)

        btn = Button(self.root, text="Reset!", command=lambda: self.reset_clicked('space'),
                     width=int(5 * self.resolution), font=self.font,
                     highlightthickness=0, bd=0)
        btn.grid(row=2, column=2)

        # label and buttons to go right
        lbl = CustomFontLabel(self.root, text="Gestures to go right", font_path='resources/nidsans-webfont.ttf',
                              bg='#95cc71', fg='#1b3848', width=int(250 * self.resolution))
        lbl.grid(row=3, column=1, columnspan=2, padx=5, sticky=W, ipady=2.5)

        btn = Button(self.root, text="Train!", command=lambda: self.start_clicked('right'),
                     width=int(5 * self.resolution), font=self.font,
                     highlightthickness=0, bd=0)
        btn.grid(row=4, column=1)

        btn = Button(self.root, text="Reset!", command=lambda: self.reset_clicked('space'),
                     width=int(5 * self.resolution), font=self.font,
                     highlightthickness=0, bd=0)
        btn.grid(row=4, column=2)

        # label and buttons to shoot
        lbl = CustomFontLabel(self.root, text="Gestures to shoot", font_path='resources/nidsans-webfont.ttf',
                              bg='#95cc71', fg='#1b3848', width=int(250 * self.resolution))
        lbl.grid(row=5, column=1, columnspan=2, padx=5, sticky=W, ipady=2.5)

        btn = Button(self.root, text="Train!", command=lambda: self.start_clicked('space'),
                     width=int(5 * self.resolution), font=self.font,
                     highlightthickness=0, bd=0)
        btn.grid(row=6, column=1)

        btn = Button(self.root, text="Reset!", command=lambda: self.reset_clicked('space'),
                     width=int(5 * self.resolution), font=self.font,
                     highlightthickness=0, bd=0)
        btn.grid(row=6, column=2)

        # id
        lbl = CustomFontLabel(self.root, text="id: ", font_path='resources/nidsans-webfont.ttf',
                              fg='#ffffff', bg="#51ffff")
        lbl.grid(row=10, column=0, sticky=W, padx=10, rowspan=3, pady=10)
        self.txt = Text(self.root, height=1, width=int(7 * self.resolution), font=("Helvetica", 20))
        self.txt.grid(row=10, column=0, sticky=W, padx=50, rowspan=3, pady=10)

        # space invader
        btn = Button(self.root, text="Start space invader", command=self.start_space_invaders,
                     width=int(30 * self.resolution), font=self.font,
                     height=2, highlightthickness=0, bd=0, bg="#51ffff")
        btn.grid(row=10, column=0, columnspan=3, rowspan=3, pady=10)

        # last_score
        lbl = CustomFontLabel(self.root, text="Last score:",
                              font_path='resources/nidsans-webfont.ttf',
                              bg='#95cc71', fg='#1b3848', width=int(250 * self.resolution))
        lbl.grid(row=0, column=3, padx=5, ipady=2.5, sticky=S)

        lbl = CustomFontLabel(self.root, text="{} - {}".format(str(self.last_id), str(self.last_score)),
                              font_path='resources/nidsans-webfont.ttf',
                              bg='#95cc71', fg='#1b3848', width=int(250 * self.resolution))
        lbl.grid(row=1, column=3, padx=5, ipady=2.5, sticky=N)
        # ranking
        lbl = CustomFontLabel(self.root, text="TOP-5 RANK:", font_path='resources/nidsans-webfont.ttf',
                              bg='#95cc71', fg='#1b3848', width=int(250 * self.resolution))
        lbl.grid(row=2, column=3, padx=5, sticky=S, ipady=2.5, pady=5)

        self.display_ranking()

        self.root.wm_title("Supernova: Space invader")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.exit)
        # self.root.configure(background='#0e1c24')

    def video_loop(self):
        try:
            frame = cv2.flip(self.video_stream.frame, 1)
            # image = self.convert(self.video_stream.frame)
            if not self.ai_manager.training:
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
                                        1, (255, 255, 255), 1, cv2.LINE_AA)
                    """frame = cv2.rectangle(frame, (int((width / 2) - 202), 8), (int((width / 2) + 202), 32),
                                          (72, 56, 27), 2)"""
                    frame = cv2.rectangle(frame, (int((width / 2) - 202), 8),
                                          (int((width / 2) + 202), 32),
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
                    frame = cv2.putText(frame, text, (text_x, text_y), self.FONT, 9, (255, 255, 255), 5)
                image = self.convert(frame)

            if self.panel is None:
                self.panel = Label(image=image)
                self.panel.image = image
                self.panel.grid(row=1, rowspan=6, padx=10, pady=10)
            else:
                self.panel.configure(image=image)
                self.panel.image = image
        except RuntimeError as e:
            print("[INFO] caught a RuntimeError!")
            print(e)

        self.root.after(40, self.video_loop)

    def save_images(self):
        if self.ai_manager.training:
            if self.wait_time == 0:
                curr_frame_features = self.ai_manager.inception.get_features_from_image(self.video_stream.frame)
                self.ai_manager.train_dict.get(self.gesture).append(curr_frame_features)
                if len(self.ai_manager.train_dict.get(self.gesture)) >= 50:
                    self.stop_save()
            else:
                self.wait_time -= 1
        self.root.after(100, self.save_images)

    @staticmethod
    def convert(img):
        img = cv2.resize(img, (1000, 750))  # 640/480
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
        self.root.quit()
        exit(0)

    def start_space_invaders(self):
        if len(self.txt.get("1.0", END)) == 1:
            lbl = CustomFontLabel(self.root, text="You need to fill in your id! ",
                                  font_path='resources/nidsans-webfont.ttf', size=16,
                                  fg='#ffffff', bg="#ef5332")
            lbl.grid(column=0, row=9, columnspan=3)
        else:
            astronaut_id = self.txt.get("1.0", END)
            # company_id, astronaut_id
            """response = requests.get(
                "http://supernova.madebyartcore.com/api/checkin/{}/{}".format(self.company_id, astronaut_id))
            data = response.json()
            name = data["firstname"] + " " + data["lastname"][:1] + "." """
            name = "craftworkz"
            self.root.withdraw()
            SpaceInvaders(self.ai_manager, self.video_stream, self, astronaut_id, name).run()

    def display_ranking(self):

        lbl = CustomFontLabel(self.root, text="{} - {}".format(str(self.last_name).strip(), str(self.last_score)),
                              font_path='resources/nidsans-webfont.ttf',
                              bg='#95cc71', fg='#1b3848', width=int(250 * self.resolution))
        lbl.grid(row=1, column=3, padx=5, ipady=2.5, sticky=N)

        # check if the last score is in top 5
        if sorted(self.ranking.values())[0] < self.last_score:
            self.ranking[str(self.last_id).strip()] = self.last_score
            self.name_list[str(self.last_id).strip()] = self.last_name
            remove_id = sorted(self.ranking, key=self.ranking.__getitem__)[0]
            del self.ranking[remove_id]
            del self.name_list[remove_id]

        position = ['N', '', 'S', 'N', '']
        i = 0
        for key in sorted(self.ranking, key=self.ranking.__getitem__, reverse=True):
            if i < 3:
                lbl = CustomFontLabel(self.root,
                                      text="{} - {}".format(str(self.name_list[key]), str(self.ranking[key])),
                                      font_path='resources/nidsans-webfont.ttf',
                                      bg='#95cc71', fg='#1b3848', width=int(250 * self.resolution))
                lbl.grid(row=3, column=3, padx=5, sticky=position[i], ipady=2.5, pady=2.5)
                i += 1
            else:
                lbl = CustomFontLabel(self.root,
                                      text="{} - {}".format(str(self.name_list[key]), str(self.ranking[key])),
                                      font_path='resources/nidsans-webfont.ttf',
                                      bg='#95cc71', fg='#1b3848', width=int(250 * self.resolution))
                lbl.grid(row=4, column=3, padx=5, sticky=position[i], ipady=2.5, pady=5)
                i += 1

    def reset(self, astronaut_id, score, name):
        self.last_id = astronaut_id
        self.last_score = score
        self.last_name = name
        self.display_ranking()
        self.txt.delete('1.0', END)
        self.root.deiconify()


class CustomFontLabel(Label):
    text_size = 25

    def __init__(self, master, text, foreground="black", true_type_font=None, font_path=None, size=text_size, **kwargs):
        if true_type_font is None:
            if font_path is None:
                raise ValueError("Font path can't be None")

            # Initialize font
            true_type_font = ImageFont.truetype(font_path, size)
        width, height = true_type_font.getsize(text)

        image = Image.new("RGBA", (width, height), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        draw.text((0, 0), text, font=true_type_font, fill=foreground)

        self._photoimage = ImageTk.PhotoImage(image)
        Label.__init__(self, master, image=self._photoimage, **kwargs)
