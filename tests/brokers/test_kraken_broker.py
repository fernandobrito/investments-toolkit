from pprint import pprint

import pytest

from investmentstk.brokers import KrakenBroker


@pytest.mark.manual
class TestKrakenBroker:
    @pytest.fixture
    def subject(self) -> KrakenBroker:
        return KrakenBroker()

    def test_retrieve_balance(self, subject):
        balance = subject.retrieve_balance()

        print("Kraken balance:")
        pprint(balance)

        assert balance.currency == "EUR"
        assert balance.balance >= 1000

    def test_retrieve_stop_losses(self, subject):
        stop_losses = subject.retrieve_stop_losses()

        print("Kraken stop losses:")
        pprint(stop_losses)

        assert (len(stop_losses)) >= 1
