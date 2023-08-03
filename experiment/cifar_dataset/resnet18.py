'''
ResNet18/34/50/101/152 in TensorFlow2.

Reference:
[1] He, Kaiming, et al.
    "Deep residual learning for image recognition."
    Proceedings of the IEEE conference on computer vision and pattern recognition. 2016.
'''
import tensorflow as tf

from asynfed.client.frameworks.tensorflow import TensorflowSequentialModel
from asynfed.client.config_structure import LearningRateConfig

class BasicBlock(tf.keras.Model):
    expansion = 1

    def __init__(self, in_channels, out_channels, strides=1):
        super(BasicBlock, self).__init__()
        self.conv1 = tf.keras.layers.Conv2D(out_channels, kernel_size=3, strides=strides, padding='same', use_bias=False)
        self.bn1 = tf.keras.layers.BatchNormalization()
        self.conv2 = tf.keras.layers.Conv2D(out_channels, kernel_size=3, strides=1, padding='same', use_bias=False)
        self.bn2 = tf.keras.layers.BatchNormalization()

        if strides != 1 or in_channels != self.expansion * out_channels:
            self.shortcut = tf.keras.Sequential([
                tf.keras.layers.Conv2D(self.expansion * out_channels, kernel_size=1, strides=strides, use_bias=False),
                tf.keras.layers.BatchNormalization()
            ])
        else:
            self.shortcut = lambda x: x

    def call(self, x):
        out = tf.keras.activations.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out = tf.keras.layers.add([self.shortcut(x), out])
        out = tf.keras.activations.relu(out)
        return out


class Resnet18(TensorflowSequentialModel):
    def __init__(self, input_features = (32, 32, 3), output_features = 10, lr_config: dict = None):
        lr_config = lr_config or {}
        self.lr_config = LearningRateConfig(**lr_config)
        print("Config in the resnet model")
        print(self.lr_config.to_dict())
        super().__init__(input_features=input_features, output_features=output_features)

        print(f"Learning rate right now is: {self.get_learning_rate()}")


    def get_optimizer(self):
        return self.optimizer
    
    
    def set_learning_rate(self, lr):
        return self.optimizer.lr.assign(lr)

    def get_learning_rate(self):
        return self.optimizer.lr.numpy()


    def create_model(self, input_features, output_features):
        self.in_channels = 64
        num_blocks = [2, 2, 2, 2]

        self.conv1 = tf.keras.layers.Conv2D(64, kernel_size=3, strides=1, padding='same', use_bias=False, input_shape= input_features)
        self.bn1 = tf.keras.layers.BatchNormalization()
        self.layer1 = self._make_layer(BasicBlock, 64, num_blocks[0], strides=1)
        self.layer2 = self._make_layer(BasicBlock, 128, num_blocks[1], strides=2)
        self.layer3 = self._make_layer(BasicBlock, 256, num_blocks[2], strides=2)
        self.layer4 = self._make_layer(BasicBlock, 512, num_blocks[3], strides=2)
        self.avg_pool2d = tf.keras.layers.AveragePooling2D(pool_size=4)
        self.flatten = tf.keras.layers.Flatten()
        self.fc = tf.keras.layers.Dense(output_features, activation='softmax')

    def call(self, x):
        x = tf.cast(x, tf.float32)
        out = tf.keras.activations.relu(self.bn1(self.conv1(x)))
        out = self.layer1(out)
        out = self.layer2(out)
        out = self.layer3(out)
        out = self.layer4(out)
        out = self.avg_pool2d(out)
        out = self.flatten(out)
        out = self.fc(out)
        return out

    def create_loss_object(self):
        return tf.keras.losses.CategoricalCrossentropy()

    def create_optimizer(self):
        if self.lr_config.fix_lr:
            optimizer = tf.keras.optimizers.SGD(learning_rate= self.lr_config.lr, momentum= 0.9)
            print(f"Create optimizer with fix learning rate: {optimizer.lr.numpy()}")
        else:
            lr_scheduler = tf.keras.experimental.CosineDecay(initial_learning_rate= self.lr_config.lr,
                                                         decay_steps= self.lr_config.decay_steps)
            optimizer = tf.keras.optimizers.SGD(learning_rate=lr_scheduler, momentum=0.9)
            print(f"Create optimizer with decay learning rate: {optimizer.lr.numpy()}")

        return optimizer


    def create_train_metric(self):
        return tf.keras.metrics.CategoricalAccuracy(name='train_accuracy'), tf.keras.metrics.Mean(
            name='train_loss')

    def create_test_metric(self):
        return tf.keras.metrics.CategoricalAccuracy(name='test_accuracy'), tf.keras.metrics.Mean(name='test_loss')

    def get_train_performance(self):
        return float(self.train_performance.result())

    def get_train_loss(self):
        return float(self.train_loss.result())

    def get_test_performance(self):
        return float(self.test_performance.result())

    def get_test_loss(self):
        return float(self.test_loss.result())

    def _make_layer(self, block, out_channels, num_blocks, strides):
        stride = [strides] + [1] * (num_blocks - 1)
        layer = []
        for s in stride:
            layer += [block(self.in_channels, out_channels, s)]
            self.in_channels = out_channels * block.expansion
        return tf.keras.Sequential(layer)


