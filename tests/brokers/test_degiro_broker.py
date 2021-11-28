from pprint import pprint

import pytest

from investmentstk.brokers import DegiroBroker


@pytest.mark.manual
class TestDegiroaBroker:
    @pytest.fixture(scope="class")
    def subject(self) -> DegiroBroker:
        return DegiroBroker()

    def test_retrieve_balance(self, subject):
        balance = subject.retrieve_balance()

        print("Degiro balance:")
        pprint(balance)

        assert balance.currency == "SEK"
        assert balance.balance >= 10000

    def test_retrieve_stop_losses(self, subject):
        stop_losses = subject.retrieve_stop_losses()

        print("Degiro stop losses:")
        pprint(stop_losses)

        assert (len(stop_losses)) >= 1
