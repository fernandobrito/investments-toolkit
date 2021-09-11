from plotly.graph_objs import Figure


def show_figure(figure: Figure, *, interactive: bool = True) -> None:
    """
    Enables figures to be displayed interactively or statically.
    """
    if interactive:
        figure.show()
    else:
        figure.show("png")
