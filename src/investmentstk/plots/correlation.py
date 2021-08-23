import numpy as np
import plotly.express as px
import scipy.cluster.hierarchy as sch


def plot_correlation_matrix(dataframe, *, interactive=False, **kwargs):
    """
    Useful references:
    * https://towardsdatascience.com/better-heatmaps-and-correlation-matrix-plots-in-python-41445d0f2bec
    * https://stackoverflow.com/questions/52787431/create-clusters-using-correlation-matrix-in-python
    * https://github.com/TheLoneNut/CorrelationMatrixClustering/blob/master/CorrelationMatrixClustering.ipynb

    :param interactive:
    :param dataframe:
    :return:
    """
    fig = px.imshow(dataframe, zmin=-1, zmax=1, color_continuous_scale="rdbu", **kwargs)

    if interactive:
        fig.show()
    else:
        fig.show("png")


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


def cluster_by_correlation(df):
    correlations = df.corr().values
    distances = sch.distance.pdist(correlations)  # vector of ('55' choose 2) pairwise distances
    links = sch.linkage(distances, method="complete")
    ind = sch.fcluster(links, 0.5 * distances.max(), "distance")
    columns = [df.columns.tolist()[i] for i in list((np.argsort(ind)))]
    df = df.reindex(columns, axis=1)

    return df


def format_tick_values(boundaries):
    return [np.mean(boundaries[k : k + 2]) for k in range(len(boundaries) - 1)]


def format_tick_text(boundaries):
    return (
        [f"<{boundaries[1]}"]
        + [f"{boundaries[k]}-{boundaries[k + 1]}" for k in range(1, len(boundaries) - 2)]
        + [f">{boundaries[-2]}"]
    )
