from enum import Enum
from tempfile import SpooledTemporaryFile
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, PlainTextResponse

from investmentstk.figures import correlation
from investmentstk.figures.correlation import cluster_by_correlation
from investmentstk.models.asset import Asset
from investmentstk.models.bar import barset_to_dataframe
from investmentstk.utils.dataframe import convert_to_pct_change, merge_dataframes

app = FastAPI()


class OutputFormat(str, Enum):
    Graph = "g"
    CSV = "csv"


@app.get("/")
async def root():
    return {"status": "ok"}


@app.get("/correlations")
async def correlations(p: str, i: Optional[str] = None, f: OutputFormat = OutputFormat.CSV):
    """


    Example:
    http://localhost:8000/correlations?p=NN:5325,AV:5442,AV:26607,AV:5537&f=g
    http://localhost:8000/correlations?p=NN:5325,AV:5442,AV:26607,AV:5537&f=csv

    :param p: CSV of assets in the portfolio, in the format AV:XXXX,AV:YYYY,CMC:ZZZZ
    :param i: optional CSV of assets of interest
    :param f: output format. Either "g" for Graph (standalone HTML page with Plotly graph) or "csv" for plain
    text with CSV
    :return:
    """
    portfolio: list[Asset] = [Asset.from_id(fqn_id) for fqn_id in p.split(",") if fqn_id != "" and fqn_id != ":"]

    assets_dfs = []

    for asset in portfolio:
        bars = asset.retrieve_prices()
        df = barset_to_dataframe(bars, asset)
        assets_dfs.append(df)

    df = merge_dataframes(assets_dfs)
    df = convert_to_pct_change(df)

    clustered_df = cluster_by_correlation(df)
    clustered_df_corr = clustered_df.corr()

    if f != OutputFormat.Graph:
        # return JSONResponse(dict(col1=[1, 2, 3, 4], col2=[5, 6, 7, 8, 9], col3=dict(subcol=[1, 2, 3])))
        return PlainTextResponse(clustered_df_corr.to_csv(sep=";"))

    figure = correlation.generate_binned_figure(clustered_df_corr)

    with SpooledTemporaryFile(mode="w+") as in_memory_file:
        figure.write_html(in_memory_file, include_plotlyjs="cdn", full_html=True, auto_open=False)
        in_memory_file.seek(0)

        return HTMLResponse(in_memory_file.read())
