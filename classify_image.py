import argparse
import numpy as np
import cv2
import os
from inception_classifier import InceptionClassifier
from knn_classifier import KnnClassifier
from webcam import WebcamStream


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
    class_names = ['left', 'right', 'shoot']

    features, classes = load_images_from_folder(args.folder)

    knn = KnnClassifier(features, classes)
    predicted_class, probability = knn.predict_proba_for_image_features(None, class_names)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('model', type=str, help='Path to the model a protobuf (.pb) file.')
    parser.add_argument('--video_src', type=int, help='The index of the video source.', default=0)

    args = parser.parse_args()

    classifier = InceptionClassifier(args.model)
    webcam = WebcamStream(args.video_src)

    main(args)
