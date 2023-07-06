import os
import sys
from dotenv import load_dotenv
import pause
from apscheduler.schedulers.background import BackgroundScheduler
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.getcwd())))))
sys.path.append(root)

# from asynfed.commons.conf import Config

from asynfed.client.algorithms import ClientAsyncFl
from asynfed.client.frameworks.tensorflow import TensorflowFramework

from resnet18 import Resnet18
from data_preprocessing import preprocess_dataset

load_dotenv()

scheduler = BackgroundScheduler()

config = {
    "client_id": "234-gpu-2",
    "role": "train",
    "queue_consumer": {
        'exchange_name': 'asynfl_exchange',
        'exchange_type': 'topic',
        'queue_name': 'server_queue',
        'routing_key': 'client.#',
        'end_point': 'amqps://gocktdwu:jYQBoATqKHRqXaV4O9TahpPcbd8xjcaw@armadillo.rmq.cloudamqp.com/gocktdwu'
    },
    "queue_producer": {
        'exchange_name': 'asynfl_exchange',
        'exchange_type': 'topic',
        'queue_name': 'server_consumer',
        'routing_key': 'server.#',
        'end_point': "amqps://gocktdwu:jYQBoATqKHRqXaV4O9TahpPcbd8xjcaw@armadillo.rmq.cloudamqp.com/gocktdwu"
    },

    "training_params": {
        "dataset": "cifar10",
        "model": "resnet18",

        "min_acc": 0.80,
        "min_epoch": 100,

        "regularization": "l2",
        "lambda_value": 5e-4,
        "learning_rate": 1e-1,
        "beta": 0.6,


        # setup differently for different device
        "gpu_index": 1,
        "chunk_index": 5,

        "qod": 0.45,
        "batch_size": 128,
        "epoch": 600,

        "tracking_point": 4000,
        "sleeping_time": 10,
        "delta_time": 1000000
    }
}

import tensorflow as tf
print("*" * 20)
if tf.config.list_physical_devices('GPU'):
    tf.config.set_visible_devices(tf.config.list_physical_devices('GPU')[config["training_params"]['gpu_index']], 'GPU')
    print("Using GPU: ", tf.config.list_physical_devices('GPU')[config["training_params"]['gpu_index']])
else:
    print("Using CPU")
print("*" * 20)

# ------------oOo--------------------
# Preprocessing data
# default_training_dataset_path = "../../../../data/cifar_data/5_chunks/chunk_2.pickle"
default_testing_dataset_path = "../../../../data/cifar_data/test_set.pickle"
training_dataset_path = f"../../../../data/cifar_data/5_chunks/chunk_{config['training_params']['chunk_index']}.pickle"
# if os.getenv("cifar_train_dataset_path"):
#     training_dataset_path = os.getenv("cifar_train_dataset_path")
# else:
#     training_dataset_path = default_training_dataset_path
    

# train_ds, data_size = preprocess_dataset(training_dataset_path, training = True)
# test_ds, _ = preprocess_dataset(testing_dataset_path, training = False)
train_ds, data_size = preprocess_dataset(training_dataset_path, batch_size = 128, training = True)
test_ds, _ = preprocess_dataset(default_testing_dataset_path, training = False)
# train_ds, data_size = preprocess_dataset("training_process/data/cifar_data/5_chunks/chunk_2.pickle", training = True)
# test_ds, _ = preprocess_dataset("training_process/data/cifar_data/test_set.pickle", training = False)
# ------------oOo--------------------

print("-" * 20)
print("-" * 20)
print(f"Begin training proceess with data size of {data_size}")
print("-" * 20)
print("-" * 20)

# Define model
model = Resnet18(input_features= (32, 32, 3), 
                 output_features= 10,
                 lr=config['training_params']['learning_rate'],
                 decay_steps= int(200 * data_size / config['training_params']['batch_size']))
                #  decay_steps=int(config['training_params']['epoch'] * data_size / config['training_params']['batch_size']))
# Define framework
tensorflow_framework = TensorflowFramework(model=model, 
                                           data_size= data_size, 
                                           train_ds= train_ds, 
                                           test_ds= test_ds, 
                                           config=config)


# tf_client = ClientAsyncFl(model=tensorflow_framework,config=config)
tf_client = ClientAsyncFl(model=tensorflow_framework,config=config, save_log=True)

tf_client.start()

scheduler.start()
pause.days(1) # or it can anything as per your need