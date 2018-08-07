import cv2
import os
import time
from pyautogui import press
from inception_classifier import InceptionClassifier
from knn_classifier import KnnClassifier


class AiManager:
    THRESHOLD = 0.8
    CLASS_NAMES = ['left', 'right', 'space']
    training = False

    def __init__(self, inception_location, train_data_location):
        self.inception = InceptionClassifier(inception_location)
        dict = self.load_images_into_dict(train_data_location)
        features, classes = self.get_features_and_classes_from_dict(dict)

        self.knn = KnnClassifier(features, classes)

    def get_features_and_classes_from_dict(self, train_dict):
        classes = []
        image_features = []
        for key in sorted(train_dict.keys()):
            for feature in train_dict[key]:
                image_features.append(feature)
                classes.append(key)

        return image_features, classes

    def load_images_into_dict(self, image_folder):
        train_dict = {'left': [], 'right': [], 'space': []}
        for dir in sorted(os.listdir(image_folder)):
            if os.path.isdir(os.path.join(image_folder, dir)):
                for file in os.listdir(os.path.join(image_folder, dir)):
                    if os.path.isfile(os.path.join(image_folder, dir, file)) and 'jpg' in file:
                        print('Calculating features for: {}'.format(os.path.join(image_folder, dir, file)))
                        image = cv2.imread(os.path.join(image_folder, dir, file))
                        image_feature = self.inception.get_features_from_image(image)
                        train_dict[dir].append(image_feature)
        return train_dict

    def classify_gesture_on_image(self, image):
        start = time.time()
        image_features = self.inception.get_features_from_image(image)
        predicted_class, probability = self.knn.predict_proba_for_image_features(image_features, self.CLASS_NAMES)
        print('Time to analyze frame: {} ms'.format((time.time() - start) * 1000))
        print(predicted_class, probability)
        if probability > self.THRESHOLD:
            press(predicted_class)

        return predicted_class, probability
