import os
import sys
from dotenv import load_dotenv
import argparse

# run locally without install asynfed package
root = os.path.dirname(os.path.dirname(os.path.dirname(os.getcwd())))
sys.path.append(root)
from asynfed.client.algorithms.client_asyncfL import ClientAsyncFl
from asynfed.commons.conf import Config

# tensorflow 
# from asynfed.client.frameworks.tensorflow.tensorflow_framework import TensorflowFramework
from custom_tensorflow_framework import CustomTensorflowFramework
from data_preprocessing import load_training_dataset
from VGG16 import VGG16


# Create an argument parser
parser = argparse.ArgumentParser(description='Example script with command-line arguments.')
# Add arguments
parser.add_argument('--queue_url', dest='queue_url', type=str, help='specify the url of RabbitMQ server')
parser.add_argument('--training_exchange', dest='training_exchange', type=str, help='define training exchange to connect to rabbitMQ server')
# Parse the arguments
args = parser.parse_args()

# load env variables
load_dotenv()

Config.QUEUE_URL = os.getenv("queue_url")
if args.queue_url:
    Config.QUEUE_URL = args.queue_url

Config.TRAINING_EXCHANGE = os.getenv("training_exchange")
if args.training_exchange:
    Config.TRAINING_EXCHANGE = args.training_exchange

# ------------oOo--------------------


if os.getenv("batch_size"):
    Config.BATCH_SIZE = int(os.getenv("batch_size"))
else:
    Config.BATCH_SIZE = 128

if os.getenv("data_size"):
    Config.DATA_SIZE = int(os.getenv("data_size"))
else:
    Config.DATA_SIZE = 60000

if os.getenv("epoch"):
    Config.EPOCH = int(os.getenv("epoch"))
else:
    Config.EPOCH = 5

if os.getenv("delta_time"):
    Config.DELTA_TIME = int(os.getenv("delta_time"))
else:
    Config.DELTA_TIME = 15


# for tracking process when training
if os.getenv("tracking_point"):
    Config.TRACKING_POINT = int(os.getenv("tracking_point"))
else:
    Config.TRACKING_POINT = 10000

if os.getenv("sleeping_time"):
    Config.SLEEPING_TIME= int(os.getenv("sleeping_time"))
else:
    Config.SLEEPING_TIME= 3

# preprocessing data to be ready for low level tensorflow training process
# Preprocessing data
# mnist dataset
# Set the file paths for the MNIST digit dataset files
data_path = "../../data/cifar_data/chunks/chunk_1.pickle"
train_ds, test_ds = load_training_dataset(train_dataset_path= data_path)


# set qod
qod = 0.45


# define model
vgg_model = VGG16(input_features = (32, 32, 3), output_features = 10)
# define framework
tensorflow_framework = CustomTensorflowFramework(model = vgg_model, epoch= Config.EPOCH, delta_time= Config.DELTA_TIME, data_size= Config.DATA_SIZE, qod= qod, train_ds= train_ds, test_ds= test_ds)

tf_client = ClientAsyncFl(model=tensorflow_framework)
tf_client.run()
