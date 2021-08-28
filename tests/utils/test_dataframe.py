import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from investmentstk.utils.dataframe import convert_to_pct_change


class TestConvertToPctChange:
    def test_trivial(self):
        df = pd.DataFrame(dict(col1=[1, 2, 4, 12], col2=[1, 4, 2, 1]))
        df = convert_to_pct_change(df)

        expected = pd.DataFrame(dict(col1=[np.nan, 1, 1, 2], col2=[np.nan, 3, -0.5, -0.5]))

        assert_frame_equal(df, expected)

    # TODO: Add a test for dataframes with gaps
