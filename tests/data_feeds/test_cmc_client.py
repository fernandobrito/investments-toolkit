import pytest

from investmentstk.data_feeds.cmc_client import CMCClient
from investmentstk.models.asset import Asset
from investmentstk.models.source import Source


@pytest.fixture
def subject() -> CMCClient:
    return CMCClient()


@pytest.fixture
def nasdaq() -> Asset:
    return Asset(Source.CMC, 'X-ABFMB', 'US NDAQ 100 - Cash')


@pytest.mark.external_http
def test_retrieve_bars(subject, nasdaq):
    bars = subject.retrieve_bars(nasdaq.source_id)

    first_bar = list(bars)[0]

    assert len(bars) > 0
    assert (first_bar.high >= first_bar.low)


@pytest.mark.external_http
def test_retrieve_asset_name(subject, nasdaq):
    name = subject.retrieve_asset_name(nasdaq.source_id)
    assert name == nasdaq.name


@pytest.mark.external_http
def test_retrieve_price(subject, nasdaq):
    price = subject.retrieve_price(nasdaq.source_id)
    assert 10000 <= price.last <= 20000
    assert -1000 <= price.change <= 1000
    assert -10 <= price.change_pct <= 10
