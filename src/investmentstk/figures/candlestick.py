from datetime import timedelta, date

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

    # figure = go.Figure(data=[candlestick_chart])
    figure = make_subplots(rows=2, cols=1, row_heights=[0.8, 0.2])

    figure.add_trace(candlestick_chart, row=1, col=1)

    # Not easy to find good linear dtick with a log scale
    data_range = dataframe["close"].max() - dataframe["close"].min()
    figure.update_yaxes(row=1, col=1, type="log", dtick=f"L{data_range / 10}")

    figure.update_layout(xaxis_rangeslider_visible=False)

    figure.update_layout(title=f"{asset.name}: Candlestick chart")

    if "stop" in dataframe.columns:
        # TODO: only needed for daily charts. Find a way to figure it out from here
        # figure.update_xaxes(rangebreaks=[dict(values=list(date_gaps(dataframe)))])

        # Plotly doesn't support one line chart with multiple colors. The recommended solution
        # is to have 2 different traces.

        figure.add_scatter(
            x=dataframe.index,
            y=dataframe["stop"].where(dataframe["close"] < dataframe["stop"]),
            mode="lines",
            line_color="red",
            line_dash="dash",
            name="Stop loss (short)",
            row=1,
            col=1,
        )

        figure.add_scatter(
            x=dataframe.index,
            y=dataframe["stop"].where(dataframe["close"] > dataframe["stop"]),
            mode="lines",
            line_color="green",
            line_dash="dash",
            name="Stop loss (long)",
            row=1,
            col=1,
        )

        figure.add_scatter(
            x=dataframe.index, y=dataframe["atr"], mode="lines", line_color="black", name="ATR", row=2, col=1
        )

        figure.update_layout(title=f"{asset.name}: Trailing stop loss (ATR indicator)")

    figure.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))

    # Unifies the tooltips from multiple traces belonging to the same subplot into 1
    figure.update_layout(hovermode="x unified")

    # Extends the spike line for both subplots
    # Found on https://community.plotly.com/t/unified-hovermode-with-sublots/37606
    figure.update_traces(xaxis="x1")

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
