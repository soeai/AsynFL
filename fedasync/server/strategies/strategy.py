from typing import List, Dict
from abc import ABC, abstractmethod


class Strategy(ABC):
    """
    This here the Interface of strategy, follow the strategy design pattern.
    Any new strategy will follow this interface. 
    """

    @abstractmethod
    def initialize_parameters(self):
        pass

    @abstractmethod
    def select_client(self, all_clients) -> List[str]:
        """ Implement the client selection logic by 
        """

    @abstractmethod
    def aggregate(self, weights) -> None:
        """Aggregate algorithm.
        """

    @abstractmethod
    def evaluate(self):
        """Evaluate the current parameters
        """

    @abstractmethod
    def get_model_weights(self):
        """
        """

    @abstractmethod
    def set_model_weights(self, weights):
        pass

    @abstractmethod
    def data_preprocessing(self):
        pass
