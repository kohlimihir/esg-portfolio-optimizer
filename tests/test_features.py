import pandas as pd
from esg_model.processing.features import _zscore_by_group


def test_zscore_by_group_zero_mean():
    s = pd.Series([1, 2, 3, 10, 20, 30])
    g = pd.Series(["a", "a", "a", "b", "b", "b"])
    z = _zscore_by_group(s, g)
    assert abs(z.groupby(g).mean().sum()) < 1e-9


def test_zscore_handles_constant():
    s = pd.Series([5, 5, 5])
    g = pd.Series(["x", "x", "x"])
    z = _zscore_by_group(s, g)
    assert z.abs().max() < 1e-6
