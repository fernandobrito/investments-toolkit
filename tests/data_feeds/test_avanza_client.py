import pytest

from investmentstk.data_feeds.avanza_client import AvanzaClient
from investmentstk.models.asset import Asset
from investmentstk.models.source import Source


@pytest.fixture
def subject() -> AvanzaClient:
    return AvanzaClient()


@pytest.fixture
def volvo() -> Asset:
    return Asset(Source.Avanza, '5269', 'VOLV B')


def test_retrieve_bars(subject, volvo):
    bars = subject.retrieve_bars(volvo.source_id)

    first_bar = list(bars)[0]

    assert len(bars) > 0
    assert (first_bar.high >= first_bar.low)


def test_retrieve_asset_name(subject, volvo):
    name = subject.retrieve_asset_name(volvo.source_id)
    assert name == volvo.name
