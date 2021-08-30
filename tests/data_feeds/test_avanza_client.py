import pytest

from investmentstk.data_feeds.avanza_client import AvanzaClient
from investmentstk.models.asset import Asset
from investmentstk.models.source import Source


@pytest.fixture
def subject() -> AvanzaClient:
    return AvanzaClient()


@pytest.fixture
def volvo() -> Asset:
    return Asset(Source.Avanza, "5269", "VOLV B")


@pytest.mark.external_http
def test_retrieve_bars(subject, volvo):
    bars = subject.retrieve_bars(volvo.source_id)

    first_bar = list(bars)[0]

    assert len(bars) > 0
    assert first_bar.high >= first_bar.low


@pytest.mark.external_http
def test_retrieve_asset_name(subject, volvo):
    name = subject.retrieve_asset_name(volvo.source_id)
    assert name == volvo.name


@pytest.mark.external_http
def test_retrieve_price(subject, volvo):
    price = subject.retrieve_price(volvo.source_id)
    assert 100 <= price.last <= 300
    assert -10 <= price.change <= 10
    assert -10 <= price.change_pct <= 10
