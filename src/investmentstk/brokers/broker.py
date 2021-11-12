from abc import ABC, abstractmethod


class Broker(ABC):
    @property
    @abstractmethod
    def friendly_name(self):
        """
        Example: Avanza, Kraken, DeGiro
        """

    @abstractmethod
    def retrieve_balance(self):
        """

        :return:
        """
