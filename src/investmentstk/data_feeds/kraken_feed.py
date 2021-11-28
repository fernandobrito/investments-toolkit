import pandas as pd
import requests
import time
from datetime import datetime, timedelta
from typing import Optional, Mapping

from investmentstk.data_feeds.data_feed import DataFeed, TimeResolution

# Measured in minutes
from investmentstk.models.bar import Bar
from investmentstk.models.barset import BarSet, barset_to_ohlc_dataframe
from investmentstk.models.price import Price
from investmentstk.persistence.requests_cache import requests_cache_configured
from investmentstk.utils.dataframe import convert_daily_ohlc_to_weekly, convert_daily_ohlc_to_monthly

TIME_RESOLUTION_TO_KRAKEN_API_RESOLUTION_MAP = {
    TimeResolution.day: 24 * 60,  # Maximum (720 bars)
    TimeResolution.week: -1,  # Maximum (720 bars)
    TimeResolution.month: -1,  # Not supported by the API
}

TIME_RESOLUTION_TO_KRAKEN_API_TIME_RANGE_MAP = {
    TimeResolution.day: 0,  # 6 months
    TimeResolution.week: -1,  # 2 years
    TimeResolution.month: -1,  # Not supported by the API
}


class KrakenFeed(DataFeed):
    """
    A client to retrieve data from Kraken's public API.

    The API does not support month as time resolution for OHLC data, and even when using week,
    it returned weeks starting on Thursday. This class always uses day as time resolution and
    converts the results to week or month depending using pandas resample().
    """

    @requests_cache_configured()
    def _retrieve_bars(
        self, source_id: str, *, resolution: TimeResolution = TimeResolution.day, instrument_type: Optional[str] = None
    ) -> BarSet:
        """
        https://docs.kraken.com/rest/#operation/getOHLCData
        """
        if resolution == TimeResolution.month:
            raise NotImplementedError("Kraken feed API does not support monthly OHLC")

        response = requests.get(
            "https://api.kraken.com/0/public/OHLC",
            params=dict(
                pair=source_id, interval=str(TIME_RESOLUTION_TO_KRAKEN_API_RESOLUTION_MAP[resolution]), since="0"
            ),
        )

        response.raise_for_status()
        data = response.json()

        if data["error"]:
            raise RuntimeError(f'Something went wrong: {data["error"]}')

        bars: BarSet = set()
        data = data["result"]

        # Result has only 2 keys: "last" and an internal id of the asset. If we drop "last", only
        # what we need is left
        data.pop("last")
        data = list(data.values())[0]

        for ohlc in data:
            bars.add(self._ohlc_to_bar(ohlc))

        return bars

    @requests_cache_configured()
    def retrieve_ohlc(
        self, source_id: str, *, resolution: TimeResolution = TimeResolution.day, instrument_type: Optional[str] = None
    ) -> pd.DataFrame:
        bars = self._retrieve_bars(source_id, resolution=TimeResolution.day)
        df = barset_to_ohlc_dataframe(bars)

        if resolution == TimeResolution.week:
            return convert_daily_ohlc_to_weekly(df)

        if resolution == TimeResolution.month:
            return convert_daily_ohlc_to_monthly(df)

        return df

    @requests_cache_configured()
    def retrieve_asset_name(self, source_id: str, instrument_type: Optional[str] = None) -> str:
        """
        I couldn't find any API endpoint that returns a more descriptive name of the asset,
        so here we bypass the API and just return back the name of the asset, which in this case
        is descriptive enough
        """

        return source_id

    def retrieve_price(self, source_id: str, instrument_type: Optional[str] = None) -> Price:
        """
        There's no endpoint that already gives us the 24h change in % or absolute, so we use the
        OHLC endpoint and request hourly data for the last 24 hours.

        """
        one_day_ago = datetime.utcnow() - timedelta(hours=24)
        since = time.mktime(one_day_ago.utctimetuple())

        response = requests.get(
            "https://api.kraken.com/0/public/OHLC",
            params=dict(pair=source_id, interval="60", since=str(since)),  # hourly
        )

        response.raise_for_status()
        data = response.json()

        if data["error"]:
            raise RuntimeError(f'Something went wrong: {data["error"]}')

        data = data["result"]

        # Result has only 2 keys: "last" and an internal id of the asset. If we drop "last", only
        # what we need is left
        data.pop("last")
        data = list(data.values())[0]

        price_24h_ago = float(data[0][3])
        price_now = float(data[-1][3])

        change = price_now - price_24h_ago
        change_pct = change / price_24h_ago * 100

        return Price(last=price_now, change=change, change_pct=change_pct)

    @classmethod
    def _ohlc_to_bar(cls, ohlc: Mapping) -> Bar:
        """
        Converts a bar OHLC representation from Kraken into our
        representation.
        """
        return Bar(
            time=datetime.fromtimestamp(ohlc[0]),
            open=float(ohlc[1]),
            high=float(ohlc[2]),
            low=float(ohlc[3]),
            close=float(ohlc[4]),
        )
