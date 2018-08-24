import argparse
# from gesture_screen import Window
from webcam import WebcamStream
# from ai_manager import AiManager
from ranking_screen import RankingWindow

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('model', type=str, help='Path to the model a protobuf (.pb) file.')
    parser.add_argument('folder', type=str, help='Path to training data.')
    parser.add_argument('--video_src', type=int, help='The index of the video source.', default=0)

    args = parser.parse_args()

    stream = WebcamStream(args.video_src)
    stream.start()

    # ai_manager = AiManager(args.model, args.folder)
    #
    # ui = Window(stream, ai_manager, args.folder)
    # ui.video_loop()
    # ui.save_images()
    # ui.root.mainloop()

    rank = RankingWindow(stream)
    rank.video_loop()
    rank.root.mainloop()
