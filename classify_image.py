import argparse
import cv2
import os
import time
import threading
from user_interface import Window
from webcam import WebcamStream
from pyautogui import press
from inception_classifier import InceptionClassifier
from knn_classifier import KnnClassifier
from tkinter import *
from PIL import Image, ImageTk


def safe_data(gesture):
    time.sleep(3)
    while training:
        img_features = classifier.get_features_from_image(vs.frame)
        train_dict[gesture].append(img_features)
        time.sleep(0.1)


def stop():
    vs.stop()
    root.quit()
    exit(0)


def train_start(gesture):
    global training, safe_thread
    training = True
    train_dict[gesture].clear()
    safe_thread = threading.Thread(target=safe_data, args=(gesture,))
    safe_thread.start()


def train_stop():
    global training
    train_data = []
    train_labels = []
    for key in sorted(train_dict.keys()):
        train_data += train_dict[key]
        train_labels += [key for i in range(len(train_dict[key]))]
    knn.train_new_knn_classifier(train_data, train_labels)
    safe_thread.join()
    training = False


def classify_stream():
    while vs.ret and not training:
        start = time.time()
        image_features = classifier.get_features_from_image(vs.frame)
        predicted_class, probability = knn.predict_proba_for_image_features(image_features, class_names)
        # prediction = knn.predict_class_for_image(image_features)
        print('Time to analyze frame: {} ms'.format((time.time() - start) * 1000))
        print(predicted_class, probability)
        if probability > threshold:
            press(predicted_class)


def load_images_from_folder(folder):
    classes = []
    image_features = []
    for dir in sorted(os.listdir(folder)):
        if os.path.isdir(os.path.join(folder, dir)):
            for file in os.listdir(os.path.join(folder, dir)):
                if os.path.isfile(os.path.join(folder, dir, file)) and 'jpg' in file:
                    print('Calculating features for: {}'.format(os.path.join(folder, dir, file)))
                    image = cv2.imread(os.path.join(folder, dir, file))
                    classes.append(dir)
                    image_features.append(classifier.get_features_from_image(image))

    return image_features, classes


def video_loop():
    global panel
    try:
        frame = vs.frame
        image = convert(frame)
        if panel is None:
            panel = Label(image=image)
            panel.image = image
            panel.grid(row=1, rowspan=6, padx=10, pady=10)
        else:
            panel.configure(image=image)
            panel.image = image
    except RuntimeError as e:
        print("[INFO] caught a RuntimeError!")

    root.after(1, video_loop)


def convert(img):
    img = cv2.resize(img, (640, 480))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    img = ImageTk.PhotoImage(img)
    return img


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('model', type=str, help='Path to the model a protobuf (.pb) file.')
    parser.add_argument('folder', type=str, help='Path to training data.')
    parser.add_argument('--video_src', type=int, help='The index of the video source.', default=0)

    args = parser.parse_args()

    classifier = InceptionClassifier(args.model)

    train_dict = {'left': [], 'right': [], 'space': []}

    threshold = 0.8
    class_names = ['left', 'right', 'space']
    training = False

    safe_thread = None

    features, classes = load_images_from_folder(args.folder)

    knn = KnnClassifier(features, classes)

    vs = WebcamStream(0)
    vs.start()

    classify_thread = threading.Thread(target=classify_stream)
    classify_thread.daemon = True
    classify_thread.start()

    root = Tk()
    root.bind('<Escape>', lambda e: stop())
    panel = None
    label = Label(root, text="Click the buttons to start and stop recording gestures.")
    label.grid(row=0, columnspan=4)
    lbl = Label(root, text="Gestures to go left")
    lbl.grid(row=1, column=1, columnspan=2)
    btn = Button(root, text="Start!", command=lambda: train_start('left'))
    btn.grid(row=2, column=1, padx=10)
    btn = Button(root, text="Stop!", command=train_stop)
    btn.grid(row=2, column=2, padx=10)
    lbl = Label(root, text="Gestures to go right")
    lbl.grid(row=3, column=1, columnspan=2)
    btn = Button(root, text="Start!", command=lambda: train_start('right'))
    btn.grid(row=4, column=1, padx=10, pady=10)
    btn = Button(root, text="Stop!", command=train_stop)
    btn.grid(row=4, column=2, padx=10, pady=10)
    lbl = Label(root, text="Gestures to shoot")
    lbl.grid(row=5, column=1, columnspan=2)
    btn = Button(root, text="Start!", command=lambda: train_start('space'))
    btn.grid(row=6, column=1, padx=10, pady=10)
    btn = Button(root, text="Stop!", command=train_stop)
    btn.grid(row=6, column=2)
    root.wm_title("Supernova: Space invader")
    root.wm_protocol("WM_DELETE_WINDOW", stop)

    video_loop()
    root.mainloop()
