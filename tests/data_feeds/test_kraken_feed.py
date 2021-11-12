import pytest

from investmentstk.data_feeds import KrakenFeed
from investmentstk.data_feeds.data_feed import TimeResolution
from investmentstk.models.asset import Asset
from investmentstk.models.source import Source


@pytest.fixture
def subject() -> KrakenFeed:
    return KrakenFeed()


@pytest.fixture
def bitcoin() -> Asset:
    return Asset(Source.Kraken, "XBTEUR", "XBTEUR")


@pytest.mark.parametrize(
    "resolution, expected_possible_days_difference",
    [[TimeResolution.day, [1, 3]], [TimeResolution.week, [7]], [TimeResolution.month, [28, 29, 30, 31]]],
    ids=["day", "week", "month"],
)
@pytest.mark.external_http
def test_retrieve_ohlc(subject, bitcoin, resolution, expected_possible_days_difference):
    dataframe = subject.retrieve_ohlc(bitcoin.source_id, resolution=resolution)

    first_bar = dataframe.iloc[0]
    second_bar = dataframe.iloc[1]

    assert len(dataframe) > 0
    assert first_bar.high >= first_bar.low
    assert (second_bar.name - first_bar.name).days in expected_possible_days_difference


@pytest.mark.external_http
def test_retrieve_asset_name(subject, bitcoin):
    name = subject.retrieve_asset_name(bitcoin.source_id)
    assert name == bitcoin.name


@pytest.mark.external_http
def test_retrieve_price(subject, bitcoin):
    price = subject.retrieve_price(bitcoin.source_id)
    assert 30000 <= price.last <= 80000
    assert -2000 <= price.change <= 2000
    assert -10 <= price.change_pct <= 10
