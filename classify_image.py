import argparse
import tensorflow as tf
import numpy as np
import cv2
import os
from sklearn.neighbors import KNeighborsClassifier


class ImageClassification:
    def __init__(self, pb_model_location: str, gpu_memory_fraction: float = 0.6):
        gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=gpu_memory_fraction)
        with tf.Graph().as_default():
            with tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False)) as self.sess:
                self.load_model(pb_model_location)
                # Retrieve the required input and output tensors for classification from the model
                self.image_placeholder_tensor = self.sess.graph.get_tensor_by_name('DecodeJpeg:0')
                self.softmax_tensor = self.sess.graph.get_tensor_by_name('softmax:0')
                self.pool_3_tensor = self.sess.graph.get_tensor_by_name('pool_3:0')

    def load_model(self, model_location):
        with tf.gfile.FastGFile(model_location, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            tf.import_graph_def(graph_def, input_map=None, name='')

    def classify_image(self, image):
        predictions = self.sess.run(self.softmax_tensor, {self.image_placeholder_tensor: image})
        return np.squeeze(predictions)

    def get_features_from_image(self, image):
        features = self.sess.run(self.pool_3_tensor, {self.image_placeholder_tensor: image})
        return np.squeeze(features)


def train_knn_classifier(folder):
    knn_classifier = KNeighborsClassifier(n_neighbors=2)
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

    knn_classifier.fit(image_features, classes)
    return knn_classifier


def main(args):
    class_names = ['left', 'right', 'shoot']
    knn_classifier = train_knn_classifier(args.folder)

    image = cv2.imread(args.image)
    image_feature = classifier.get_features_from_image(image)

    predictions = knn_classifier.predict_proba([image_feature])
    best_class_indices = np.argmax(predictions, axis=1)
    best_class_probabilities = predictions[np.arange(len(best_class_indices)), best_class_indices]

    for i in range(len(best_class_indices)):
        print(class_names[best_class_indices[i]], best_class_probabilities[i], sep=': ')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('model', type=str,
                        help='Path to the model a protobuf (.pb) file.')
    parser.add_argument('folder', type=str,
                        help='Path to the training data')
    parser.add_argument('image', type=str,
                        help='Path to the image to classify')

    args = parser.parse_args()
    classifier = ImageClassification(args.model)
    main(args)
