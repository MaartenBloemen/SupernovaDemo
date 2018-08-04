import tensorflow as tf
import numpy as np


class InceptionClassifier:
    def __init__(self, pb_model_location: str, gpu_memory_fraction: float = 0.6):
        gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=gpu_memory_fraction)
        with tf.Graph().as_default():
            with tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False)) as self.sess:
                self.load_model(pb_model_location)
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
