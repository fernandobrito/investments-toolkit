import json
import os
import pandas as pd
from degiro_connector.quotecast.actions.action_get_chart import ChartHelper
from degiro_connector.quotecast.api import API as QuotecastAPI
from degiro_connector.quotecast.models.quotecast_pb2 import Chart
from degiro_connector.trading.models.trading_pb2 import ProductsInfo
from typing import Optional

from investmentstk.brokers import DegiroBroker
from investmentstk.data_feeds.data_feed import DataFeed, TimeResolution
from investmentstk.models.barset import BarSet, format_ohlc_dataframe
from investmentstk.models.price import Price
from investmentstk.persistence.requests_cache import requests_cache_configured
from investmentstk.utils import calendar
from investmentstk.utils.dataframe import convert_daily_ohlc_to_weekly, convert_daily_ohlc_to_monthly


class DegiroFeed(DataFeed):
    """
    A client to retrieve data from Degiro.
    A wrapper around the degiro-connector library.

    The other feeds do not require private credentials, but this one does because there's an ID translation step
    (from product ID to an internal vwd ID) that makes use of an endpoint that requires authentication.

    Example of the different possible IDs: Microsoft

    * Product ID is the one you can see in the URL when searching for Microsoft stocks on Degiro website: 332111
    * ISIN (International Securities Identification Number) is the company ID
      and can have multiple products associated with (different exchanges): US5949181045

    For charting, Degiro uses another provider (vwd), which has 2 keys:
    * vwdId (vwd key): "MSFT.BATS,E"
    * vwdIdSecondary (issue id): "350015444"
    """

    culture = "en-US"
    timezone = "Etc/GMT"

    def __init__(self):
        credentials = json.loads(os.environ["DEGIRO_CREDENTIALS"])

        self.quotecast_api = QuotecastAPI(user_token=credentials["user_token"])
        self.broker_client = DegiroBroker()

    def _retrieve_bars(
        self, source_id: str, *, resolution: TimeResolution = TimeResolution.day, instrument_type: Optional[str] = None
    ) -> BarSet:
        raise NotImplementedError(
            "DegiroFeed uses degiro-connector which already provides methods to return a "
            "dataframe directly. Use retrieve_ohlc() instead."
        )

    @requests_cache_configured()
    def retrieve_ohlc(
        self,
        source_id: str,
        *,
        resolution: TimeResolution = TimeResolution.day,
        instrument_type: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Using P1M as resolution returns today - 1 MONTH, and not calendar months.
        Just like the KrakenFeed, we always retrieve daily from the API and convert it to
        weekly or monthly by ourselves.

        :param source_id: the internal ID used in Avanza
        :param resolution: time resolution
        :param instrument_type: not used in this Feed
        :return: a BarSet
        """
        # Translate the ID
        vwd_id = self._retrieve_vwd_id_from_product_id(int(source_id))

        # Prepare the request
        request = self._build_request()
        request.resolution = Chart.Interval.P1D
        request.period = Chart.Interval.P5Y
        request.series.append("ohlc:issueid:" + vwd_id)

        # Fetch the data
        chart = self.quotecast_api.get_chart(request=request, raw=False)

        # Format the data
        ChartHelper.format_chart(chart=chart, copy=False)
        dataframe = ChartHelper.serie_to_df(serie=chart.series[0])
        dataframe["time"] = pd.to_datetime(dataframe["timestamp"], unit="s")
        dataframe["time"] = dataframe["time"].apply(calendar.round_day)
        dataframe = dataframe.drop("timestamp", axis=1)

        dataframe = format_ohlc_dataframe(dataframe)

        if resolution == TimeResolution.week:
            return convert_daily_ohlc_to_weekly(dataframe)

        if resolution == TimeResolution.month:
            return convert_daily_ohlc_to_monthly(dataframe)

        return dataframe

    @requests_cache_configured()
    def retrieve_asset_name(self, source_id: str, instrument_type: Optional[str] = None) -> str:
        """
        Retrieves the name of an asset. Example: MSFT

        :param source_id: the internal ID (product ID) used in Degiro
        :param instrument_type: not relevant for this broker
        :return: the asset name (ticker)
        """

        product_info = self._retrieve_product_info(int(source_id))

        return product_info["symbol"]

    @requests_cache_configured(hours=0.5)
    def retrieve_price(self, source_id: str, instrument_type: Optional[str] = "stock") -> Price:
        # Translate the ID
        vwd_id = self._retrieve_vwd_id_from_product_id(int(source_id))

        # Prepare the request
        request = self._build_request()
        request.resolution = Chart.Interval.P1D
        request.period = Chart.Interval.P1W
        request.series.append("issueid:" + vwd_id)

        # Format the data
        chart = self.quotecast_api.get_chart(request=request, raw=True)

        # Format the data
        data = chart["series"][0]["data"]

        # Even though it's called lastPrice, it seems to be the close price (without after-hours market)
        # API can return None when it's 0
        last = data["lastPrice"]
        change = data["absDiff"] or 0
        change_pct = (data["relDiff"] or 0) * 100

        return Price(last=last, change=change, change_pct=change_pct)

    def _retrieve_vwd_id_from_product_id(self, product_id: int) -> str:
        """
        Translates the product ID to the vwd_id necessary for most quotecast_api operations
        """
        product_info = self._retrieve_product_info(product_id)

        return product_info["vwdIdSecondary"]

    def _retrieve_product_info(self, product_id: int) -> dict:
        request = ProductsInfo.Request()
        request.products.extend([product_id])

        products_info = self.broker_client.api_client.get_products_info(
            request=request,
            raw=True,
        )

        return products_info["data"][str(product_id)]

    def _build_request(self) -> Chart.Request:
        request = Chart.Request()
        request.culture = self.culture
        request.tz = self.timezone
        request.requestid = "1"

        return request
