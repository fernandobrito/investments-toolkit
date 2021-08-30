import pytest

from investmentstk.figures.correlation import format_tick_labels, format_tick_values


@pytest.fixture
def boundaries():
    return [-1, -0.5, 0, 0.5, 1]


def test_format_tick_values(boundaries):
    assert format_tick_values(boundaries) == [-0.75, -0.25, 0.25, 0.75]


def test_format_tick_labels(boundaries):
    assert format_tick_labels(boundaries) == ["< -0.5", "-0.5 to 0", "0 to 0.5", "> 0.5"]
