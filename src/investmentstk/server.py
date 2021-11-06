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
    """
    Useful for health checks

    :return: a simple static JSON object
    """
    return {"status": "ok"}


@app.get("/price/{fqn_id}")
def price(fqn_id: str) -> Price:
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
            asset_data = {"fqn_id": asset_fqn}

            price = _price_common(asset_fqn)
            asset_data.update(**dataclasses.asdict(price))

            output.append(asset_data)
        except json.JSONDecodeError as e:
            source, _ = Asset.parse_fqn_id(asset_fqn)
            logger.error(
                f"Exception raised. {type(e).__name__}: {e}", asset_id=asset_fqn, source=source, error=type(e).__name__
            )

    return output


def _price_common(asset_fqn: str) -> Price:
    source, source_id = Asset.parse_fqn_id(asset_fqn)
    source_client = build_data_feed_from_source(source)
    return source_client.retrieve_price(source_id)


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
            asset_data = {"fqn_id": asset_fqn}
            asset_data["stop_loss_atr"] = _stop_loss_atr_common(asset_fqn)

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
        bars = asset.retrieve_bars()
        dataframe = barset_to_single_column_dataframe(bars, asset)
        dataframes.append(dataframe)

    merged_dataframe = merge_dataframes(dataframes)

    return merged_dataframe
