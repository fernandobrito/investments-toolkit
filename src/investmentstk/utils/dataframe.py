import pandas as pd
from pandas import DataFrame


def convert_to_pct_change(dataframe: DataFrame) -> DataFrame:
    """
    Iterates over all columns of a dataframe and converts them to
    percentage changes between the current and a prior element.
    Useful to convert asset prices to % changes before calculating
    the correlation between different assets.

    :param dataframe: input dataframe
    :return: a copy of the dataframe
    """
    dataframe = dataframe.copy()
    dataframe = dataframe.sort_index()

    for column in dataframe:
        dataframe[column] = dataframe[column].pct_change()

    return dataframe


def merge_dataframes(dataframes: list[DataFrame], join: str = "outer") -> DataFrame:
    """
    Performs a join of a list of dataframes.

    :param dataframes: a list of dataframes
    :param join: the type of join
    :return:
    """
    dataframe = pd.concat(dataframes, axis="columns", join=join)

    return dataframe
