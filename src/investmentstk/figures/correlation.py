import numpy as np
import plotly.express as px
import scipy.cluster.hierarchy as sch
from pandas import DataFrame


def generate_binned_figure(dataframe, **kwargs):
    boundaries = [-1, -0.75, -0.5, -0.25, 0.25, 0.5, 0.75, 1]
    red_blue = px.colors.diverging.RdBu
    colors = [red_blue[0], red_blue[2], red_blue[4], "white", red_blue[-5], red_blue[-3], red_blue[-1]]
    colorscale = discrete_colorscale(boundaries, colors)

    boundaries = np.array(boundaries)
    tick_values = format_tick_values(boundaries)
    tick_text = format_tick_text(boundaries)

    figure = px.imshow(dataframe, zmin=-1, zmax=1, **kwargs)
    figure.layout.coloraxis1.colorscale = colorscale
    figure.layout.coloraxis1.colorbar = dict(thickness=20, tickvals=tick_values, ticktext=tick_text)

    return figure


def generate_figure(dataframe, **kwargs):
    """
    Useful references:
    * https://towardsdatascience.com/better-heatmaps-and-correlation-matrix-plots-in-python-41445d0f2bec
    * https://stackoverflow.com/questions/52787431/create-clusters-using-correlation-matrix-in-python
    * https://github.com/TheLoneNut/CorrelationMatrixClustering/blob/master/CorrelationMatrixClustering.ipynb

    :param dataframe:
    :return:
    """
    return px.imshow(dataframe, zmin=-1, zmax=1, color_continuous_scale="rdbu", **kwargs)


def show_figure(figure, *, interactive=True):
    if interactive:
        figure.show()
    else:
        figure.show("png")


def discrete_colorscale(boundaries, colors):
    """
    Creates a discrete color scale to be used on Plotly Heatmaps

    From:
    * https://community.plotly.com/t/colors-for-discrete-ranges-in-heatmaps/7780/10
    * https://chart-studio.plotly.com/~empet/15229/heatmap-with-a-discrete-colorscale/#/

    boundaries - list of values bounding intervals/ranges of interest
    colors - list of rgb or hex colorcodes for values in [bvals[k], bvals[k+1]],0<=k < len(bvals)-1
    returns the plotly  discrete colorscale
    """
    if len(boundaries) != len(colors) + 1:
        raise ValueError("len(boundary values) should be equal to  len(colors)+1")

    boundaries = sorted(boundaries)
    nvals = [(v - boundaries[0]) / (boundaries[-1] - boundaries[0]) for v in boundaries]  # normalized values

    colorscale = []  # discrete colorscale

    for k in range(len(colors)):
        colorscale.extend([[nvals[k], colors[k]], [nvals[k + 1], colors[k]]])

    return colorscale


def cluster_by_correlation(dataframe: DataFrame) -> DataFrame:
    correlations = dataframe.corr().values
    distances = sch.distance.pdist(correlations)  # vector of ('55' choose 2) pairwise distances
    links = sch.linkage(distances, method="complete")
    ind = sch.fcluster(links, 0.5 * distances.max(), "distance")
    columns = [dataframe.columns.tolist()[i] for i in list((np.argsort(ind)))]
    dataframe = dataframe.reindex(columns, axis=1)

    return dataframe


def format_tick_values(boundaries):
    return [np.mean(boundaries[k : k + 2]) for k in range(len(boundaries) - 1)]  # noqa: E203


def format_tick_text(boundaries):
    return (
        [f"<{boundaries[1]}"]
        + [f"{boundaries[k]}-{boundaries[k + 1]}" for k in range(1, len(boundaries) - 2)]
        + [f">{boundaries[-2]}"]
    )
