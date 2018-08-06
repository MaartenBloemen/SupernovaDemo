import numpy as np
from sklearn.neighbors import KNeighborsClassifier


class KnnClassifier:
    knn_classifier = None

    def __init__(self, train_data, target_classes, nrof_neighborgs=2):
        self.train_new_knn_classifier(train_data, target_classes, nrof_neighborgs)

    def train_new_knn_classifier(self, train_data, target_classes, nrof_neighborgs=2):
        self.knn_classifier = KNeighborsClassifier(n_neighbors=nrof_neighborgs)
        self.knn_classifier.fit(train_data, target_classes)

    def predict_class_for_image(self, image_features):
        prediction = self.knn_classifier.predict([image_features])
        return prediction

    def predict_proba_for_image_features(self, image_features, class_names):
        predictions = self.knn_classifier.predict_proba([image_features])
        best_class_indices = np.argmax(predictions, axis=1)
        best_class_probabilities = predictions[np.arange(len(best_class_indices)), best_class_indices]

        for i in range(len(best_class_indices)):
            return class_names[best_class_indices[i]], best_class_probabilities[i]
