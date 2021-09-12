from enum import Enum
from tempfile import SpooledTemporaryFile
from typing import Iterable, Union

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, PlainTextResponse
from pandas import DataFrame

from investmentstk.data_feeds.data_feed import TimeResolution
from investmentstk.figures import correlation
from investmentstk.figures.correlation import cluster_by_correlation
from investmentstk.formulas.average_true_range import average_true_range_trailing_stop
from investmentstk.models.asset import Asset
from investmentstk.models.barset import barset_to_single_column_dataframe, barset_to_ohlc_dataframe
from investmentstk.models.price import Price
from investmentstk.models.source import build_data_feed_from_source, Source
from investmentstk.utils.dataframe import convert_to_pct_change, merge_dataframes

app = FastAPI()


class OutputFormat(str, Enum):
    Graph = "g"
    CSV = "csv"


@app.get("/")
async def root():
    return {"status": "ok"}


@app.get("/price/{fqn_id}")
async def price(fqn_id: str) -> Price:
    """
    Returns price details (last price, % chance) of a given asset

    :param fqn_id: example: AV:XXXXX
    :return: a Price object
    """

    source, source_id = Asset.parse_fqn_id(fqn_id)
    source_client = build_data_feed_from_source(source)
    return source_client.retrieve_price(source_id)


@app.get("/stop_loss_atr/{fqn_id}")
async def stop_loss_atr(fqn_id: str) -> float:
    """
    Returns the ATR

    :param fqn_id:
    :return:
    """

    # TODO: Very specific to my trade system
    # Consider moving the default time resolution to a configuration file

    asset = Asset.from_id(fqn_id)

    if asset.source == Source.CMC:
        multiplier = 3.0
        resolution = TimeResolution.week
    else:
        multiplier = 2.5
        resolution = TimeResolution.month

    barset = asset.retrieve_bars(resolution=resolution)
    dataframe = barset_to_ohlc_dataframe(barset)
    stop_loss = average_true_range_trailing_stop(dataframe, periods=21, multiplier=multiplier)

    # Return latest closed bar
    return stop_loss["stop"][-2]


@app.get("/correlations")
async def correlations(p: str, e: str = "", f: OutputFormat = OutputFormat.CSV):
    """
    Calculates a clustered correlation matrix of assets provided in the portfolio (`p` parameter).
    If a list of external assets is provided (`e` parameter), after the clustering is done, it appends
    such assets to the list to allow for comparison.

    The output can be either a standalone HTML page with a Plotly graph or a "csv" plain text format

    Example:
    http://localhost:8000/correlations?p=NN:5325,AV:5442,AV:26607,AV:5537&f=g
    http://localhost:8000/correlations?p=NN:5325,AV:5442,AV:26607,AV:5537&f=csv

    :param p: CSV of assets in the portfolio, in the format AV:XXXX,AV:YYYY,CMC:ZZZZ
    :param e: optional CSV of "extra" assets
    :param f: output format. Either "g" for Graph (standalone HTML page with Plotly graph) or "csv" for plain
    text with CSV
    :return:
    """
    portfolio: list[Asset] = _parse_input_list(p)
    external: list[Asset] = _parse_input_list(e)

    # Prepare portfolio dataframe
    dataframe = _prepare_dataframe(portfolio)
    dataframe = convert_to_pct_change(dataframe)
    clustered_dataframe = cluster_by_correlation(dataframe)

    # Prepare and merge interest dataframe
    if external:
        interest_df = _prepare_dataframe(external)
        interest_df = convert_to_pct_change(interest_df)
        clustered_dataframe = merge_dataframes([clustered_dataframe, interest_df])

    clustered_df_corr = clustered_dataframe.corr()

    # Handles both output formats
    return _format_output(clustered_df_corr, f)


def _parse_input_list(input_list: str) -> list[Asset]:
    """
    Converts a CSV list of asset IDs into Asset objects
    """
    return [Asset.from_id(fqn_id) for fqn_id in input_list.split(",") if fqn_id != "" and fqn_id != ":"]


def _format_output(dataframe: DataFrame, format: OutputFormat) -> Union[PlainTextResponse, HTMLResponse]:
    """
    Formats a dataframe into one of the supported output formats.
    """
    if format != OutputFormat.Graph:
        return PlainTextResponse(dataframe.to_csv(sep=";"))

    figure = correlation.generate_binned_figure(dataframe)

    with SpooledTemporaryFile(mode="w+") as in_memory_file:
        figure.write_html(in_memory_file, include_plotlyjs="cdn", full_html=True, auto_open=False)
        in_memory_file.seek(0)

        return HTMLResponse(in_memory_file.read())


def _prepare_dataframe(portfolio: Iterable[Asset]) -> DataFrame:
    """
    Takes a list of Assets and returns a single dataframe with them merged
    """
    dataframes = []

    for asset in portfolio:
        bars = asset.retrieve_bars()
        dataframe = barset_to_single_column_dataframe(bars, asset)
        dataframes.append(dataframe)

    merged_dataframe = merge_dataframes(dataframes)

    return merged_dataframe
