from typing import Sequence, Any

import numpy as np
import plotly.express as px
import scipy.cluster.hierarchy as sch
from pandas import DataFrame
from plotly.graph_objs import Figure


def generate_binned_figure(dataframe: DataFrame, **kwargs) -> Figure:
    """
    High-level function to generate a binned correlation matrix Plotly figure.
    The values are only binned for the colorscale (i.e.: the data in the dataframe is not modified).
    """
    boundaries = [-1, -0.75, -0.5, -0.25, 0.25, 0.5, 0.75, 1]
    red_blue = px.colors.diverging.RdBu
    colors = [red_blue[0], red_blue[2], red_blue[4], "white", red_blue[-5], red_blue[-3], red_blue[-1]]
    colorscale = discrete_colorscale(boundaries, colors)

    tick_values = format_tick_values(boundaries)
    tick_text = format_tick_text(boundaries)

    figure = px.imshow(dataframe, zmin=-1, zmax=1, **kwargs)
    figure.layout.coloraxis1.colorscale = colorscale
    figure.layout.coloraxis1.colorbar = dict(thickness=20, tickvals=tick_values, ticktext=tick_text)

    return figure


def generate_figure(dataframe: DataFrame, **kwargs) -> Figure:
    """
    References:
    * https://towardsdatascience.com/better-heatmaps-and-correlation-matrix-plots-in-python-41445d0f2bec
    """
    return px.imshow(dataframe, zmin=-1, zmax=1, color_continuous_scale=px.colors.diverging.RdBu, **kwargs)


def show_figure(figure: Figure, *, interactive: bool = True):
    """
    Enables figures to be displayed interactively or statically.
    """
    if interactive:
        figure.show()
    else:
        figure.show("png")


def discrete_colorscale(boundaries: Sequence[float], colors: Sequence[str]) -> list[list[Any]]:
    """
    Creates a discrete color scale to be used on Plotly Heatmaps.
    It normalizes an arbitrary list of boundaries from 0 to 1.

    From:
    * https://community.plotly.com/t/colors-for-discrete-ranges-in-heatmaps/7780/10
    * https://chart-studio.plotly.com/~empet/15229/heatmap-with-a-discrete-colorscale/#/

    :param boundaries: list of values bounding intervals/ranges of interest
    :param colors: list of rgb or hex colorcodes for values in [bvals[k], bvals[k+1]],0<=k < len(bvals)-1
    :return: the plotly discrete colorscale.

    Example of return value:
    [
        [0.0, "rgb(...)"],
        [0.125, "rgb(...)],
        [0.125, "rgb(...)],
        [0.25, "rgb(...)],
        ...
    ]

    """
    if len(boundaries) != len(colors) + 1:
        raise ValueError("len(boundary values) should be equal to  len(colors)+1")

    boundaries = sorted(boundaries)
    normalized_values = [
        (v - boundaries[0]) / (boundaries[-1] - boundaries[0]) for v in boundaries
    ]

    colorscale: list[list[Any]] = []

    for k in range(len(colors)):
        colorscale.extend([[normalized_values[k], colors[k]], [normalized_values[k + 1], colors[k]]])

    return colorscale


def cluster_by_correlation(dataframe: DataFrame) -> DataFrame:
    """
    Reorders a dataframe grouping/clustering highly clustered rows together.

    Heavily inspired by from:
    * https://stackoverflow.com/questions/52787431/create-clusters-using-correlation-matrix-in-python
    * https://github.com/TheLoneNut/CorrelationMatrixClustering/blob/master/CorrelationMatrixClustering.ipynb
    """
    # Calculates the clusters
    correlations = dataframe.corr().values
    distances = sch.distance.pdist(correlations)
    links = sch.linkage(distances, method="complete")
    ind = sch.fcluster(links, 0.5 * distances.max(), "distance")

    # Reorders the dataframe
    columns = [dataframe.columns.tolist()[i] for i in list((np.argsort(ind)))]
    dataframe = dataframe.reindex(columns, axis=1)

    return dataframe


def format_tick_values(boundaries: Sequence[float]) -> list[float]:
    """
    Formats the tick values from the boundaries to be used to position the tick text in the color legend of the graph.
    Tick texts are position in the middle of the range.

    Example: for boundaries [-1, 0, 1], ticks will be in -0.5 and 0.5
    """
    return [np.mean(boundaries[k: k + 2]) for k in range(len(boundaries) - 1)]  # noqa: E203


def format_tick_text(boundaries: Sequence[float]) -> list[str]:
    """
    Creates tick texts from the boundaries to be used in the color legend of the graph.

    Example: < -0.75, -0.75 to -0.50, -0.50 to -0.25, ...
    """
    return (
        [f"<{boundaries[1]}"]
        + [f"{boundaries[k]} to {boundaries[k + 1]}" for k in range(1, len(boundaries) - 2)]
        + [f">{boundaries[-2]}"]
    )
