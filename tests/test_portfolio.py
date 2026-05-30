import pandas as pd
from esg_model.portfolio.constructor import build_target_weights


def test_weights_sum_to_one():
    scores = pd.DataFrame({
        "ticker": [f"T{i}" for i in range(20)],
        "sector": ["A"] * 10 + ["B"] * 10,
        "esg_score": list(range(20)),
    })
    w = build_target_weights(scores)
    assert abs(w["weight"].sum() - 1.0) < 1e-6
    assert (w["weight"] >= 0).all()
