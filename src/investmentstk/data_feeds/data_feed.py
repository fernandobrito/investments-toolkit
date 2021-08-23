from abc import ABC, abstractmethod

from investmentstk.models.bar import BarSet


class DataFeed(ABC):
    """
    Abstract class that every data feed client should implement.

    Individual instances be created by a factory method in `models/source.py`
    """

    @abstractmethod
    def retrieve_bars(self, source_id: str) -> BarSet:
        """
        Retrieve bars. For now, very simple implementation and not flexible at all
        (in terms of time range and periodicity).

        :param source_id: the if for the asset in the source
        :return: a BarSet
        """
        ...
