import pytest

from investmentstk.data_feeds import CMCFeed
from investmentstk.data_feeds.data_feed import TimeResolution
from investmentstk.models.asset import Asset
from investmentstk.models.source import Source


@pytest.fixture
def subject() -> CMCFeed:
    return CMCFeed()


@pytest.fixture
def nasdaq() -> Asset:
    return Asset(Source.CMC, "X-ABFMB", "US NDAQ 100 - Cash")


@pytest.mark.external_http
def test_retrieve_ohlc(subject, nasdaq):
    dataframe = subject.retrieve_ohlc(nasdaq.source_id, resolution=TimeResolution.day)

    first_bar = dataframe.iloc[0]

    # Basic sanity tests
    assert len(dataframe) > 0
    assert first_bar["high"] >= first_bar["low"]

    # Test that days of the week are correct
    days_of_week = set(dataframe.index.map(lambda ts: ts.strftime("%A")))
    assert len(days_of_week & {"Saturday", "Sunday"}) == 0


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
