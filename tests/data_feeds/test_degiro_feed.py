import pytest

from investmentstk.data_feeds import DegiroFeed
from investmentstk.data_feeds.data_feed import TimeResolution
from investmentstk.models.asset import Asset
from investmentstk.models.source import Source


@pytest.mark.manual
class TestDegiroFeed:
    @pytest.fixture(scope="class")
    def subject(self) -> DegiroFeed:
        return DegiroFeed()

    @pytest.fixture
    def msft(self) -> Asset:
        return Asset(Source.Degiro, "332111", "MSFT")

    @pytest.mark.parametrize(
        "resolution, expected_possible_days_difference",
        [[TimeResolution.day, [1, 3]], [TimeResolution.week, [7]], [TimeResolution.month, [28, 29, 30, 31]]],
        ids=["day", "week", "month"],
    )
    @pytest.mark.external_http
    def test_retrieve_ohlc(self, subject, msft, resolution, expected_possible_days_difference):
        dataframe = subject.retrieve_ohlc(msft.source_id, resolution=resolution)

        first_bar = dataframe.iloc[0]
        second_bar = dataframe.iloc[1]

        assert len(dataframe) > 0
        assert first_bar.high >= first_bar.low
        assert (second_bar.name - first_bar.name).days in expected_possible_days_difference

    def test_retrieve_price(self, subject, msft):
        price = subject.retrieve_price(msft.source_id)

        assert 200 <= price.last <= 500
        assert -50 <= price.change <= 50
        assert -10 <= price.change_pct <= 10

    def test_retrieve_asset_name(self, subject, msft):
        name = subject.retrieve_asset_name(msft.source_id)

        assert name == msft.name

    def test__retrieve_vwd_id_from_product_id(self, subject, msft):
        vwd_id = subject._retrieve_vwd_id_from_product_id(int(msft.source_id))

        assert vwd_id == "350015444"
