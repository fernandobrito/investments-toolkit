from enum import Enum

import json
import nbformat
import papermill
import requests
import requests.exceptions
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, PlainTextResponse
from nbconvert import HTMLExporter
from pandas import DataFrame
from pathlib import Path
from tempfile import SpooledTemporaryFile, NamedTemporaryFile
from typing import Iterable, Union

from investmentstk.brokers import AvanzaBroker, KrakenBroker, DegiroBroker
from investmentstk.data_feeds.data_feed import TimeResolution
from investmentstk.figures import correlation
from investmentstk.figures.correlation import cluster_by_correlation
from investmentstk.formulas.average_true_range import atr_stop_loss_from_asset
from investmentstk.models.asset import Asset
from investmentstk.models.barset import ohlc_to_single_column_dataframe
from investmentstk.persistence.requests_cache import delete_cached_requests
from investmentstk.utils.dataframe import convert_to_pct_change, merge_dataframes
from investmentstk.utils.logger import get_logger

app = FastAPI()

current_folder = Path(__file__).resolve().parent

logger = get_logger()


class OutputFormat(str, Enum):
    Graph = "g"
    CSV = "csv"


@app.get("/")
async def root():
    """
    Useful for health checks

    :return: a simple static JSON object
    """
    return {"status": "ok"}


@app.get("/price/{fqn_id}")
def price(fqn_id: str) -> dict:
    """
    Returns price details (last price, % chance) of a given asset

    :param fqn_id: example: AV:XXXXX
    :return: a Price object
    """

    return _price_common(fqn_id)


@app.get("/price_bulk")
def price_bulk(p: str) -> list:
    assets_fqn = _parse_input_list(p)
    output = []

    for asset_fqn in assets_fqn:
        try:
            price = _price_common(asset_fqn)

            output.append(price)
        except (json.JSONDecodeError, requests.HTTPError) as e:
            source, _ = Asset.parse_fqn_id(asset_fqn)
            logger.error(
                f"Exception raised. {type(e).__name__}: {e}", asset_id=asset_fqn, source=source, error=type(e).__name__
            )

    return output


def _price_common(asset_fqn: str) -> dict:
    asset = Asset.from_id(asset_fqn)
    price = asset.retrieve_price()

    return price


@app.get("/stop_losses_broker")
def stop_losses_broker(skip_cache: bool = False) -> list:
    """
    Returns all current stop losses in the supported brokers.

    :return: JSON object with fqn_id's and the stop loss price
    """
    brokers = [AvanzaBroker, DegiroBroker, KrakenBroker]

    output = []

    for broker_class in brokers:
        try:
            stop_losses = broker_class(skip_cache=skip_cache).retrieve_stop_losses()
            stop_losses = [stop_loss.to_response() for stop_loss in stop_losses]
            output.extend(stop_losses)
        except requests.HTTPError as e:
            logger.error(
                f"Exception raised. {type(e).__name__}: {e}", client=broker_class.__name__, error=type(e).__name__
            )

    return output


@app.get("/balance_brokers")
def balance_brokers(skip_cache: bool = False):
    brokers = [AvanzaBroker, DegiroBroker, KrakenBroker]

    output = []

    for broker_class in brokers:
        try:
            broker = broker_class(skip_cache=skip_cache)
            balance = broker.retrieve_balance()
            output.append({"broker": broker.friendly_name, **balance.dict()})
        except requests.HTTPError as e:
            logger.error(
                f"Exception raised. {type(e).__name__}: {e}", client=broker_class.__name__, error=type(e).__name__
            )

    return output


@app.get("/stop_loss_atr/{fqn_id}")
def stop_loss_atr(fqn_id: str) -> float:
    """
    Returns the stop loss calculated using an ATR trailing stop

    :param fqn_id: example: AV:XXXXXX
    :return: the stop loss price
    """

    return _stop_loss_atr_common(fqn_id)


@app.get("/stop_loss_atr_bulk")
def stop_loss_atr_bulk(p: str) -> list:
    assets_fqn = _parse_input_list(p)
    output = []

    for asset_fqn in assets_fqn:
        try:
            asset_data = {"fqn_id": asset_fqn, "stop_loss_atr": _stop_loss_atr_common(asset_fqn)}

            output.append(asset_data)
        except (json.JSONDecodeError, requests.exceptions.HTTPError) as e:
            source, _ = Asset.parse_fqn_id(asset_fqn)
            logger.error(
                f"Exception raised. {type(e).__name__}: {e}", asset_id=asset_fqn, source=source, error=type(e).__name__
            )

    return output


def _stop_loss_atr_common(asset_fqn: str):
    asset = Asset.from_id(asset_fqn)
    stop_loss = atr_stop_loss_from_asset(asset)

    # Return latest closed bar
    return stop_loss["stop"][-1]


@app.get("/stop_losses_report")
def stop_losses_report(p: str, all: bool = False):
    """
    Generates a HTML report with stop losses for all the assets provided.

    :param p: CSV of assets in the portfolio, in the format AV:XXXX,AV:YYYY,CMC:ZZZZ
    :param all: whether to include all assets or only the relevant ones
               (weekends only showing weekly-based assets, monthly only showing monthly-based assets)
    :return:
    """
    template_path = current_folder / "templates" / "stop_loss_report.ipynb"

    assets_fqn = _parse_input_list(p)

    with NamedTemporaryFile(mode="w+") as temp_file:
        # Use the given list of assets as a parameter in the notebook
        papermill.execute_notebook(
            template_path,
            temp_file.name,
            progress_bar=False,
            parameters=dict(assets=assets_fqn, show_all=all),
            report_mode=True,  # Add metadata to input cells
        )

        # Hide cells that have the metadata setted above
        HTMLExporter.exclude_input = True
        HTMLExporter.exclude_markdown = True
        html_exporter = HTMLExporter(template_name="classic")

        # Export the notebook as HTML
        notebook = nbformat.read(temp_file, as_version=4)
        (body, resources) = html_exporter.from_notebook_node(notebook)

        return HTMLResponse(body)


@app.get("/correlations")
def correlations(p: str, e: str = "", f: OutputFormat = OutputFormat.CSV):
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
    :return: either a CSV with the raw correlations or a HTML page with the Plotly graph
    """
    portfolio: list[Asset] = _input_list_to_assets(p)
    external: list[Asset] = _input_list_to_assets(e)

    # Prepare portfolio dataframe
    dataframe = _prepare_dataframe(portfolio)
    dataframe = convert_to_pct_change(dataframe)
    clustered_dataframe = cluster_by_correlation(dataframe)

    # Prepare and merge interest dataframe
    if external:
        external_df = _prepare_dataframe(external)
        external_df = convert_to_pct_change(external_df)
        clustered_dataframe = merge_dataframes([clustered_dataframe, external_df])

    clustered_df_corr = clustered_dataframe.corr()

    # Handles both output formats
    return _format_output(clustered_df_corr, f)


@app.get("/clear_cache")
def clear_cache() -> list[str]:
    return delete_cached_requests()


def _parse_input_list(input_list: str) -> list[str]:
    """
    Converts a CSV list of assets IDs into a list of parsed IDs (but not Asset objects)
    """
    return [fqn_id for fqn_id in input_list.split(",") if fqn_id != "" and fqn_id != ":"]


def _input_list_to_assets(input_list: str) -> list[Asset]:
    """
    Converts a CSV list of asset IDs into Asset objects
    """
    parsed_input = _parse_input_list(input_list)
    return [Asset.from_id(fqn_id) for fqn_id in parsed_input]


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
        dataframe = asset.retrieve_ohlc(resolution=TimeResolution.day)
        dataframe = ohlc_to_single_column_dataframe(dataframe, asset)
        dataframes.append(dataframe)

    merged_dataframe = merge_dataframes(dataframes)
    merged_dataframe = merged_dataframe.sort_index()
    merged_dataframe = merged_dataframe.tail(261)  # business days in a year

    return merged_dataframe
