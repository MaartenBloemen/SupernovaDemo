from tkinter import *
import tkinter.font as tkFont
from PIL import Image, ImageFont, ImageDraw, ImageTk
from spaceinvaders_simple import SpaceInvaders
import math
import cv2
import requests
import json
import datetime
from ranking_screen import RankingWindow

class Window:
    FONT = cv2.FONT_HERSHEY_SIMPLEX

    training = False
    gesture = None
    wait_time = 30

    def __init__(self, tkFrame, video_stream, ai_manager, save_location, ranking_screen: RankingWindow):
        self.ranking_screen = ranking_screen
        self.root = tkFrame
        self.ai_manager = ai_manager
        self.video_stream = video_stream
        self.save_location = save_location

        self.resolution = 1.76666
        self.company_id = "LNXOG3I5"
        self.last_score = -1
        self.last_id = -1    # ""5b7d6f2de6879"
        self.last_name = "John doe"

        # self.root = Tk()
        # self.root.attributes("-FULLSCREEN", True)
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
        logo_lbl.grid(row=14, column=3, rowspan=3, columnspan=2, padx=10, pady=10)

        self.panel = None
        # id valid text
        self.lbl = None

        label = CustomFontLabel(self.root, text="Click the buttons to start and stop recording gestures.",
                                font_path='resources/nidsans-webfont.ttf', size=30, bg='#51ffff',
                                fg='#1b3848', width=1920)
        label.grid(row=0, columnspan=5, pady=5, ipady=5)

        # label and buttons to go left
        lbl = CustomFontLabel(self.root, text="Gestures to go left", font_path='resources/nidsans-webfont.ttf',
                              bg='#95cc71', fg='#1b3848', width=300)
        lbl.grid(row=1, column=1, columnspan=2, ipady=5, padx=15, sticky=N + S + E + W)

        btn = Button(self.root, text="Train!", command=lambda: self.start_clicked('left'),
                     width=8, font=self.font,
                     highlightthickness=0, bd=0)
        btn.grid(row=2, column=1)

        btn = Button(self.root, text="Reset!", command=lambda: self.reset_clicked('space'),
                     width=8, font=self.font,
                     highlightthickness=0, bd=0)
        btn.grid(row=2, column=2)

        # label and buttons to go right
        lbl = CustomFontLabel(self.root, text="Gestures to go right", font_path='resources/nidsans-webfont.ttf',
                              bg='#95cc71', fg='#1b3848', width=300)
        lbl.grid(row=6, column=1, columnspan=2, ipady=5, padx=15, sticky=N + S + E + W)

        btn = Button(self.root, text="Train!", command=lambda: self.start_clicked('right'),
                     width=8, font=self.font,
                     highlightthickness=0, bd=0)
        btn.grid(row=7, column=1)

        btn = Button(self.root, text="Reset!", command=lambda: self.reset_clicked('space'),
                     width=8, font=self.font,
                     highlightthickness=0, bd=0)
        btn.grid(row=7, column=2)

        # label and buttons to shoot
        lbl = CustomFontLabel(self.root, text="Gestures to shoot", font_path='resources/nidsans-webfont.ttf',
                              bg='#95cc71', fg='#1b3848', width=300)
        lbl.grid(row=11, column=1, columnspan=2, ipady=5, padx=15, sticky=N + S + E + W)

        btn = Button(self.root, text="Train!", command=lambda: self.start_clicked('space'),
                     width=8, font=self.font,
                     highlightthickness=0, bd=0)
        btn.grid(row=12, column=1)

        btn = Button(self.root, text="Reset!", command=lambda: self.reset_clicked('space'),
                     width=8, font=self.font,
                     highlightthickness=0, bd=0)
        btn.grid(row=12, column=2)

        # id
        lbl = CustomFontLabel(self.root, text="             astronaut id: ", size=30,
                              font_path='resources/nidsans-webfont.ttf',
                              bg='#0e1c24', foreground='#3a97a9', anchor='w')
        lbl.grid(row=14, column=0, sticky=W + E + N + S, ipadx=20)
        self.txt = Text(self.root, height=1, width=15, font=("Helvetica", 25))
        self.txt.grid(row=14, column=0)
        self.txt.bind('<Return>', lambda e: self.start_space_invaders())

        # space invader
        lbl = CustomFontLabel(self.root, text=" ", size=30,
                              font_path='resources/nidsans-webfont.ttf',
                              bg='#0e1c24', foreground='#3a97a9', anchor='w')
        lbl.grid(row=15, column=0, sticky=W + E + N + S, ipadx=20)
        btn = Button(self.root, text="Start space invader", command=self.start_space_invaders,
                     width=30, font=self.font,
                     highlightthickness=0, bd=0, bg="#51ffff")
        btn.grid(row=15, column=0)

        # last_score
        lbl = CustomFontLabel(self.root, text="Last score:", size=40,
                              font_path='resources/nidsans-webfont.ttf',
                              bg='#95cc71', foreground='#0e1c24', width=550)
        lbl.grid(row=1, column=3, columnspan=2, sticky=N + S, padx=10)

        # ranking
        lbl = CustomFontLabel(self.root, text="TOP-5 RANK TODAY:", size=40, font_path='resources/nidsans-webfont.ttf',
                              bg='#95cc71', foreground='#0e1c24', width=550)
        lbl.grid(row=7, column=3, columnspan=2, sticky=N + S, padx=10)

        self.display_ranking()

        self.root.wm_title("Supernova: Space invader")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.exit)
        # self.root.configure(background='#0e1c24')

    def video_loop(self):
        try:
            frame = cv2.flip(self.video_stream.frame, 1)
            # frame = self.video_stream.frame
            self.ranking_screen.video_loop(frame, False)
            # cv2.imwrite('resources/stream/image.JPEG', frame)
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
                self.panel = Label(self.root, image=image)
                self.panel.image = image
                self.panel.grid(row=1, rowspan=12, padx=10, pady=10)
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
            if self.lbl is not None:
                self.lbl.destroy()
            self.lbl = CustomFontLabel(self.root, text="You need to fill in your id! ",
                                  font_path='resources/nidsans-webfont.ttf', size=16,
                                  fg='#ffffff', bg="#ef5332")
            self.lbl.grid(column=0, row=15, sticky=N)
        else:
            astronaut_id = self.txt.get("1.0", END).strip()
            print(astronaut_id)
            if astronaut_id == '-1':
                SpaceInvaders(self.ai_manager, self.video_stream, self, astronaut_id, 'demo', self.ranking_screen).run()
            else:
                # company_id, astronaut_id
                url = "http://supernova.madebyartcore.com/api/checkin/{}/{}".format(self.company_id, astronaut_id).strip()
                print(url)
                response = requests.get(url)
                data = response.json()
                print("_" * 50)
                print(data)
                print("_" * 50)
                if data["code"] == 400:
                    if not data["errors"]["astronautFound"]:
                        if self.lbl is not None:
                            self.lbl.destroy()
                        self.lbl = CustomFontLabel(self.root,
                                              text="Your astronaut id is invalid! ",
                                              font_path='resources/nidsans-webfont.ttf', size=16,
                                              fg='#ffffff', bg="#ef5332")
                        self.lbl.grid(column=0, row=15, sticky=N)
                    elif data["errors"]["alreadyCheckedIn"]:
                        if self.lbl is not None:
                            self.lbl.destroy()
                        self.lbl = CustomFontLabel(self.root,
                                              text="You already explored this planet! ",
                                              font_path='resources/nidsans-webfont.ttf', size=16,
                                              fg='#ffffff', bg="#ef5332")
                        self.lbl.grid(column=0, row=15, sticky=N)
                        name = "craftworkz"
                        self.root.withdraw()
                        SpaceInvaders(self.ai_manager, self.video_stream, self, astronaut_id, name, self.ranking_screen).run()
                elif data["code"] == 200:
                    name = data["astronaut"]["firstname"] + " " + data["astronaut"]["lastname"]
                    # name = "craftworkz"
                    self.root.withdraw()
                    SpaceInvaders(self.ai_manager, self.video_stream, self, astronaut_id, name, self.ranking_screen).run()
        return 'break'

    def display_ranking(self):
        now = datetime.datetime.now()
        date = now.strftime("%d-%m")

        lbl = CustomFontLabel(self.root, text="{}".format(str(self.last_name).strip()),
                              font_path='resources/nidsans-webfont.ttf',
                              bg='#0e1c24', foreground='#3a97a9', width=450)
        lbl.grid(row=2, column=3, sticky=N + S + E)
        lbl = CustomFontLabel(self.root, text="{}p".format(str(self.last_score)),
                              font_path='resources/nidsans-webfont.ttf',
                              bg='#0e1c24', foreground='#3a97a9', width=100)
        lbl.grid(row=2, column=4, sticky=N + S + W)

        with open('resources/json_files/ranking_all.json') as json_file:
            astronaut_list_all = json.load(json_file)
            sorted_list_all = sorted(astronaut_list_all, key=lambda astronaut: int(astronaut['score']))

        try:
            with open('resources/json_files/ranking_' + date + '.json') as json_file:
                astronaut_list_day = json.load(json_file)
                sorted_list_day = sorted(astronaut_list_day, key=lambda astronaut: int(astronaut['score']))
        except FileNotFoundError:
            with open('resources/json_files/ranking_' + date + '.json', 'w') as new_json_file:
                with open('resources/json_files/ranking_day_original.json') as ranking_original:
                    data = json.load(ranking_original)
                json.dump(data, new_json_file)
                print(data)
            sorted_list_day = sorted(data, key=lambda astronaut: int(astronaut['score']))


        # check if the last score is in top 5
        if int(sorted_list_day[0]['score']) < self.last_score:
            del sorted_list_day[0]
            astronaut_id = self.last_id
            name = self.last_name
            score = self.last_score
            sorted_list_day.append({
                "id": astronaut_id,
                "name": name,
                "score": score,
                "date": date
            })

            # check if the last score is in top 20
            if int(sorted_list_all[0]['score']) < self.last_score:
                del sorted_list_all[0]
                astronaut_id = self.last_id
                name = self.last_name
                score = self.last_score
                sorted_list_all.append({
                    "id": astronaut_id,
                    "name": name,
                    "score": score,
                    "date": date
                })

        i = 0
        sorted_five = sorted(sorted_list_day, key=lambda astronaut: int(astronaut['score']), reverse=True)[:5]
        for astro in sorted_five:
            if i < 3:
                lbl = CustomFontLabel(self.root,
                                      text="{}".format(astro['name']),
                                      font_path='resources/nidsans-webfont.ttf',
                                      bg='#0e1c24', foreground='#3a97a9', width=450)
                lbl.grid(row=8 + i, column=3, sticky=N + S + E)
                lbl = CustomFontLabel(self.root,
                                      text="{}p".format(astro['score']),
                                      font_path='resources/nidsans-webfont.ttf',
                                      bg='#0e1c24', foreground='#3a97a9', width=100)
                lbl.grid(row=8 + i, column=4, sticky=N + S + W)
                i += 1
            else:
                lbl = CustomFontLabel(self.root,
                                      text="{}".format(astro['name']),
                                      font_path='resources/nidsans-webfont.ttf',
                                      bg='#0e1c24', foreground='#3a97a9', width=450)
                lbl.grid(row=8 + i, column=3, sticky=N + S + E)
                lbl = CustomFontLabel(self.root,
                                      text="{}p".format(astro['score']),
                                      font_path='resources/nidsans-webfont.ttf',
                                      bg='#0e1c24', foreground='#3a97a9', width=100)
                lbl.grid(row=8 + i, column=4, sticky=N + S + W)
                i += 1

        with open('resources/json_files/ranking_all.json', 'w') as json_file:
            json.dump(sorted_list_all, json_file)
        with open('resources/json_files/ranking_' + date + '.json', 'w') as json_file:
            json.dump(sorted_list_day, json_file)
        self.ranking_screen.display_ranking()

    def reset(self, astronaut_id, score, name):
        if astronaut_id != '-1':
            self.last_id = astronaut_id
            self.last_score = score
            self.last_name = name
            self.display_ranking()
        if self.lbl is not None:
            self.lbl.destroy()
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
