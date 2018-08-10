from tkinter import *
from user_interface import Window


class CheckIn:

    def __init__(self, video_stream, ai_manager, save_location):
        self.ai_manager = ai_manager
        self.video_stream = video_stream
        self.save_location = save_location

        self.root = Tk()
        self.root.bind('<Escape>', lambda e: self.exit())

        btn = Button(self.root, text="Continue to the gestures", command=self.gestures_screen)
        btn.place(x=0, y=0)

        self.root.wm_title("Supernova: Space invader")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.exit)

    def gestures_screen(self):
        next_screen = Window(self.video_stream, self.ai_manager, self.save_location)
        next_screen.video_loop()
        next_screen.save_images()
        next_screen.root.mainloop()

    def exit(self):
        self.video_stream.stop()
        self.root.quit()
        exit(0)