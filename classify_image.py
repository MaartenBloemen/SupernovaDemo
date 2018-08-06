import argparse
import cv2
import os
import time
from pyautogui import press
from inception_classifier import InceptionClassifier
from knn_classifier import KnnClassifier


def load_images_from_folder(folder):
    classes = []
    image_features = []
    for dir in os.listdir(folder):
        if os.path.isdir(os.path.join(folder, dir)):
            for file in os.listdir(os.path.join(folder, dir)):
                if os.path.isfile(os.path.join(folder, dir, file)) and 'jpg' in file:
                    print('Calculating features for: {}'.format(os.path.join(folder, dir, file)))
                    image = cv2.imread(os.path.join(folder, dir, file))
                    classes.append(dir)
                    image_features.append(classifier.get_features_from_image(image))

    return image_features, classes


def main(args):
    threshold = 0.8
    class_names = ['left', 'right', 'space']

    features, classes = load_images_from_folder('/home/maarten/Documents/SupernovaTest')

    knn = KnnClassifier(features, classes)
    vc = cv2.VideoCapture(0)
    rval, frame = vc.read()

    while rval:
        start = time.time()
        image_features = classifier.get_features_from_image(frame)
        predicted_class, probability = knn.predict_proba_for_image_features(image_features, class_names)
        print('Time to analyze frame: {} ms'.format((time.time() - start) * 1000))
        print(predicted_class, probability)
        if probability > threshold:
            press(predicted_class)
        rval, frame = vc.read()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('model', type=str, help='Path to the model a protobuf (.pb) file.')
    parser.add_argument('folder', type=str, help='Path to training data.')
    parser.add_argument('--video_src', type=int, help='The index of the video source.', default=0)

    args = parser.parse_args()

    classifier = InceptionClassifier(args.model)

    main(args)
