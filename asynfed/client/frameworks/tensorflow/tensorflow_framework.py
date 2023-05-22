import tensorflow as tf
from tensorflow.keras import Model
from ...ModelWrapper import ModelWrapper

# from .tensorflow_sequential_model import TensorflowSequentialModel

'''
    - This is a reference of how user can defined a tensorflow model
        that can be used in our platform
    - users can use our abstract class to define their own model
        or they can design one by themselves
        as long as it is inherited from class ModelWarapper
        and satify all the requirements (at least provide data_size, train_ds, and 
        implement of all abstract functions)
    - more frameworks can be found at asynfed/client/frameworks directory
'''

class TensorflowFramework(ModelWrapper):
    # Tensorflow Model must be an inheritant of class tensorflow.keras.Model
    # model, data_size, train_ds is required
    # test_ds is optional
    def __init__(self, model: Model, data_size, train_ds, test_ds):
        super().__init__()
        '''
        - model must have an optimizer, a loss object, and trainining metric 
            model.optimizer
            model.loss_object
            model.train_performance
            model.train_loss
        - if there is a test_ds, must define testing metrics 
            similar as the way we define training metrics
        - model must have function to get train_performanced and train_loss as numerical data
            model.get_train_performanced()
            model.get_train_loss()
        - if there is a test_ds, must define similar functions 
            to get test_performanced and train_performanced as numerical data
        - detail instruction on how to create a sequential model 
            for tensorflow framework can be found at tensorflow_sequential_model.py
        '''
        self.model = model
        self.data_size = data_size
        self.train_ds = train_ds
        if test_ds:
            self.test_ds = test_ds

    def set_weights(self, weights):
        return self.model.set_weights(weights)
    
    def get_weights(self):
        return self.model.get_weights()
    
    def fit(self, x, y):
        self.train_step(x, y)
        return self.model.get_train_performance(), self.model.get_train_loss()
    
    def evaluate(self, x, y):
        self.test_step(x, y)
        return self.model.get_test_performance(), self.model.get_test_loss()

    @tf.function
    def train_step(self, images, labels):
        with tf.GradientTape() as tape:
            # training=True is only needed if there are layers with different
            # behavior during training versus inference (e.g. Dropout).
            predictions = self.model(images, training=True)
            loss = self.model.loss_object(labels, predictions)
        gradients = tape.gradient(loss, self.model.trainable_variables)
        self.model.optimizer.apply_gradients(zip(gradients, self.model.trainable_variables))
        self.model.train_loss(loss)
        self.model.train_performance(labels, predictions)

    @tf.function
    def test_step(self, images, labels):
    # training=False is only needed if there are layers with different
    # behavior during training versus inference (e.g. Dropout).
        predictions = self.model(images, training=False)
        t_loss = self.model.loss_object(labels, predictions)
        self.model.test_loss(t_loss)
        self.model.test_performance(labels, predictions)

