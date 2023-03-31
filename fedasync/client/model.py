from abc import ABC, abstractmethod

from fedasync.client.client import ClientProducer
from fedasync.client.client_storage_connector import ClientStorage


class ClientModel(ABC):
    """
    - This is the abstract Client class
    - Client can extend to use with Deep frameworks like tensorflow, pytorch by extending this abstract class and
        implement it's abstract methods.
    """

    def __init__(self, model):
        # Dependencies
        self._storage_connector: ClientStorage = None
        self._producer: ClientProducer = None

        self.model = model
        self.global_model_update_data_size = 0
        self.avg_loss = 0.0
        self.global_model_name = None
        self.global_model_version = 0
        self.local_version = 0
        self.__new_model_flag = False

    # Abstract methods
    @abstractmethod
    def set_weights(self, weights):
        pass

    @abstractmethod
    def get_weights(self):
        pass

    @abstractmethod
    def train(self):
        pass

    @abstractmethod
    def evaluate(self):
        pass
