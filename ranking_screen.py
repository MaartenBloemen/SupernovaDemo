import tkinter as tk
import tkinter.font as tkFont
import cv2
from PIL import Image, ImageFont, ImageDraw, ImageTk
import json
from webcam import WebcamStream


class RankingWindow:
    def __init__(self, stream):
        self.video_stream = stream
        self.panel = None

        self.root = tk.Tk()
        self.root.bind('<Escape>', lambda e: self.exit())
        self.font = tkFont.Font(family='monospace', size=20, weight='bold')

        # background
        background_image = tk.PhotoImage(file="resources/header1.png")
        background_label = tk.Label(self.root, image=background_image)
        background_label.image = background_image
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        # craftworkz logo
        logo = tk.PhotoImage(
            file="resources/craftworkz.png")
        logo_lbl = tk.Label(self.root, image=logo)
        logo_lbl.image = logo
        logo_lbl.grid(row=14, column=5, rowspan=7, padx=62.5, pady=62.5)

        self.display_ranking()

        self.root.wm_title("Supernova: Space invader")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.exit)
        # self.root.configure(background='#0e1c24')

    def video_loop(self):
        try:
            frame = self.video_stream.frame
            # image = self.convert(self.video_stream.frame)

            image = self.convert(frame)

            if self.panel is None:
                self.panel = tk.Label(image=image)
                self.panel.image = image
                self.panel.grid(row=0, column=0, rowspan=20, padx=25)
            else:
                self.panel.configure(image=image)
                self.panel.image = image
        except RuntimeError as e:
            print("[INFO] caught a RuntimeError!")
            print(e)

        self.root.after(5, self.video_loop)

    def exit(self):
        self.video_stream.stop()
        self.root.quit()
        exit(0)

    def display_ranking(self):
        ipady = 45
        with open('resources/ranking_all.json') as json_file:
            astronaut_list = json.load(json_file)
            sorted_list = sorted(astronaut_list, key=lambda astronaut: int(astronaut['score']), reverse=True)

        lbl = CustomFontLabel(self.root,
                              text="TOP-20 OF ALL TIME",
                              font_path='resources/nidsans-webfont.ttf', bg='#95cc71', foreground='#0e1c24',
                              width=1920, size=50)
        lbl.grid(row=0, column=0, columnspan=6, ipady=5, pady=10)

        for row_index in range(1, 21):
            for column_index in range(1, 5):

                # shows index 1 - 20
                if column_index == 1:
                    lbl = CustomFontLabel(self.root,
                                          text="{}".format(str(row_index)),
                                          font_path='resources/nidsans-webfont.ttf', bg='#0e1c24', foreground='#3a97a9',
                                          width=75, height=ipady)
                    lbl.grid(row=row_index, column=column_index)

                # shows the name
                elif column_index == 2:
                    lbl = CustomFontLabel(self.root,
                                          text="{}".format(sorted_list[row_index - 1]['name']),
                                          font_path='resources/nidsans-webfont.ttf', bg='#0e1c24', foreground='#3a97a9',
                                          width=500, height=ipady, anchor='w')
                    lbl.grid(row=row_index, column=column_index)

                # shows the score
                elif column_index == 3:
                    lbl = CustomFontLabel(self.root,
                                          text="{}".format(sorted_list[row_index - 1]['score']),
                                          font_path='resources/nidsans-webfont.ttf', bg='#0e1c24', foreground='#3a97a9',
                                          width=100, height=ipady)
                    lbl.grid(row=row_index, column=column_index, )

                # shows the date
                elif column_index == 4:
                    lbl = CustomFontLabel(self.root,
                                          text='{}'.format(sorted_list[row_index - 1]['date']),
                                          font_path='resources/nidsans-webfont.ttf', bg='#0e1c24', foreground='#3a97a9',
                                          width=150, height=ipady)
                    lbl.grid(row=row_index, column=column_index)
        self.root.after(40, self.video_loop)

    @staticmethod
    def convert(img):
        img = cv2.resize(img, (720, 540))  # 640/480
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img = ImageTk.PhotoImage(img)
        return img


class CustomFontLabel(tk.Label):
    text_size = 35

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
        tk.Label.__init__(self, master, image=self._photoimage, **kwargs)


if __name__ == '__main__':
    stream = WebcamStream(0)
    stream.start()
    rank = RankingWindow(stream)
    rank.video_loop()
    rank.root.mainloop()
