import pytest

from investmentstk.data_feeds import AvanzaFeed
from investmentstk.data_feeds.data_feed import TimeResolution
from investmentstk.models.asset import Asset
from investmentstk.models.source import Source


@pytest.fixture
def subject() -> AvanzaFeed:
    return AvanzaFeed()


@pytest.fixture
def volvo() -> Asset:
    return Asset(Source.Avanza, "5269", "VOLV B")


@pytest.mark.parametrize(
    "resolution, expected_possible_days_difference",
    [[TimeResolution.day, [1, 3]], [TimeResolution.week, [7]], [TimeResolution.month, [28, 29, 30, 31]]],
    ids=["day", "week", "month"],
)
@pytest.mark.external_http
def test_retrieve_ohlc(subject, volvo, resolution, expected_possible_days_difference):
    dataframe = subject.retrieve_ohlc(volvo.source_id, resolution=resolution)

    first_bar = dataframe.iloc[0]
    second_bar = dataframe.iloc[1]

    assert len(dataframe) > 0
    assert first_bar.high >= first_bar.low
    assert (second_bar.name - first_bar.name).days in expected_possible_days_difference


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
