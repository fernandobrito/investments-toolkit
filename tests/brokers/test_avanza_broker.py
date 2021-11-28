from pprint import pprint

import pytest

from investmentstk.brokers import AvanzaBroker


@pytest.mark.manual
class TestAvanzaBroker:
    @pytest.fixture(scope="class")
    def subject(self) -> AvanzaBroker:
        return AvanzaBroker()

    def test_retrieve_balance(self, subject):
        balance = subject.retrieve_balance()

        print("Avanza balance:")
        pprint(balance)

        assert balance.currency == "SEK"
        assert balance.balance >= 10000

    def test_retrieve_stop_losses(self, subject):
        stop_losses = subject.retrieve_stop_losses()

        print("Avanza stop losses:")
        pprint(stop_losses)

        assert (len(stop_losses)) >= 1
