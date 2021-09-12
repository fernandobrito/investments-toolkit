from datetime import timedelta, date

import pandas as pd
import plotly.graph_objects as go

from investmentstk.data_feeds.data_feed import TimeResolution
from investmentstk.models.asset import Asset


def generate_figure(dataframe: pd.DataFrame, asset: Asset) -> go.Figure:
    candlestick_chart = go.Candlestick(
        x=dataframe.index,
        open=dataframe["open"],
        high=dataframe["high"],
        low=dataframe["low"],
        close=dataframe["close"],
        name=asset.name,
    )

    figure = go.Figure(data=[candlestick_chart])

    figure.update_layout(title="Candlestick chart")

    if "stop" in dataframe.columns:
        figure.update_xaxes(rangebreaks=[dict(values=list(date_gaps(dataframe)))])

        # Plotly doesn't support one line chart with multiple colors. The recommended solution
        # is to have 2 different traces.

        figure.add_scatter(
            x=dataframe.index,
            y=dataframe["stop"].where(dataframe["close"] < dataframe["stop"]),
            mode="lines",
            line_color="red",
            line_dash="dash",
            name="Stop loss (short)",
        )

        figure.add_scatter(
            x=dataframe.index,
            y=dataframe["stop"].where(dataframe["close"] > dataframe["stop"]),
            mode="lines",
            line_color="green",
            line_dash="dash",
            name="Stop loss (long)",
        )

        figure.update_layout(title="Trailing stop loss (ATR indicator)")

    figure.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))

    return figure


def date_gaps(dataframe: pd.DataFrame, resolution: TimeResolution = TimeResolution.day) -> set[date]:
    """
    When plotting candlestick graphs on Plotly, weekends and holidays (days without bars) are shown as
    gaps in the chart. The recommended approach is to list them as "rangebreaks" in Plotly.

    This function accepts a dataframe with time as index, takes the minimum and the maximum values,
    calculates all intermediate values and returns the ones missing from the index.

    Example: if a dataframe has 4 rows: 1st, 2nd, 5th and 6th of January, this function will return
    3nd and 4th of January.
    """

    start_date = dataframe.index.min()
    end_date = dataframe.index.max()

    # Create a set with all dates between
    all_dates = {start_date + timedelta(days=index) for index in range((end_date - start_date).days + 1)}

    return all_dates - set(dataframe.index)
