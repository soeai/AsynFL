
import os
import sys
import argparse
root = os.path.dirname(os.getcwd())
sys.path.append(root)

import flwr as fl
import tensorflow as tf
from data_preprocessing import *
from resnet18 import Resnet18

def start_client(args):

    if args.gpu is not None:
        try:
            tf.config.set_visible_devices(tf.config.list_physical_devices('GPU')[args.gpu], 'GPU')
            print("Using GPU: ", tf.config.list_physical_devices('GPU')[args.gpu])
        except:
            print("GPU not found, use CPU instead")
    else:
        print("Using CPU")

    chunk = args.chunk
    train_path = f'data/chunk_{chunk}.pickle'
    test_path = 'data/test_set.pickle'

    x_train, y_train, data_size = preprocess_dataset(train_path)
    x_test, y_test, _ = preprocess_dataset(test_path)

    print('datasize: ', data_size, 'x_train shape:', x_train.shape, 'y_train shape:', y_train.shape, 'x_test shape:', x_test.shape, 'y_test shape:', y_test.shape)

    
    datagen = get_datagen()
    datagen.fit(x_train)

    # HYPERPARAMETERS
    epoch = 200
    batch_size = 128

    learning_rate = 1e-1
    lambda_value = 5e-4
    decay_steps = epoch * data_size / batch_size


    # model
    model = Resnet18(num_classes= 10)
    # Set the learning rate and decay steps
    learning_rate_fn = tf.keras.experimental.CosineDecay(learning_rate, decay_steps=decay_steps)

    # Create the SGD optimizer with L2 regularization
    optimizer = tf.keras.optimizers.SGD(learning_rate=learning_rate_fn, momentum=0.9)
    regularizer = tf.keras.regularizers.l2(lambda_value)

    # Compile the model
    model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['accuracy'], 
                loss_weights=None, weighted_metrics=None, run_eagerly=None, 
                steps_per_execution=None)
    # Build the model
    model.build(input_shape=(None, 32, 32, 3))

    # Apply L2 regularization to applicable layers
    for layer in model.layers:
        if isinstance(layer, tf.keras.layers.Conv2D) or isinstance(layer, tf.keras.layers.Dense):
            layer.kernel_regularizer = regularizer
        if hasattr(layer, 'bias_regularizer') and layer.use_bias:
            layer.bias_regularizer = regularizer


    class CifarClient(fl.client.NumPyClient):
        def get_parameters(self, config):
            return model.get_weights()

        def fit(self, parameters, config):
            model.set_weights(parameters)
            model.fit(x_train, y_train, epochs=1, batch_size=32, steps_per_epoch=args.steps_per_epoch)
            return model.get_weights(), len(x_train), {}

        def evaluate(self, parameters, config):
            model.set_weights(parameters)
            loss, accuracy, _, _, _, _ = model.evaluate(x_test, y_test, batch_size=batch_size, return_dict=False)
            return loss, len(x_test), {"accuracy": accuracy}


    fl.client.start_numpy_client(server_address=args.address, client=CifarClient())
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Federated Learning Client")
        
    parser.add_argument("--gpu", type=int, default=0, help="Specify the GPU index")
    parser.add_argument("--chunk", type=int, default=2, help="Specify the chunk size")
    parser.add_argument("--address", type=str, default="0.0.0.0:8080", help="Specify the server address")
    parser.add_argument("--steps_per_epoch", type=int, default=50, help="Specify the number of steps per epoch")

    args = parser.parse_args()
    start_client(args)


