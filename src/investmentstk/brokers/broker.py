from abc import ABC, abstractmethod

from investmentstk.models import BrokerBalance, StopLoss


class Broker(ABC):
    @property
    @abstractmethod
    def friendly_name(self):
        """
        Example: Avanza, Kraken, DeGiro
        """

    @abstractmethod
    def retrieve_balance(self) -> BrokerBalance:
        """
        Retrieves the current broker balance with the associated currency
        """

    @abstractmethod
    def retrieve_stop_losses(self) -> list[StopLoss]:
        """
        Retrieves the active stop losses
        """
