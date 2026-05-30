from __future__ import annotations
import pandas as pd
import numpy as np
from ..utils.config import load_yaml


def build_target_weights(scores: pd.DataFrame) -> pd.DataFrame:
    """Sector-neutral, top-quintile long-only weights."""
    cfg = load_yaml("portfolio_config.yaml")
    q = cfg["top_quantile"]
    max_w = cfg["max_weight"]
    
    df = scores.copy()
    df["rank"] = df.groupby("sector")["esg_score"].rank(pct=True)
    selected = df[df["rank"] >= 1 - q].copy()
    
    if cfg["sector_neutral"]:
        sector_w = 1.0 / selected["sector"].nunique()
        selected["weight"] = selected.groupby("sector")["esg_score"].transform(
            lambda s: sector_w / len(s)
        )
    else:
        selected["weight"] = 1.0 / len(selected)
    
    selected["weight"] = selected["weight"].clip(upper=max_w)
    selected["weight"] /= selected["weight"].sum()
    
    return selected[["ticker", "sector", "esg_score", "weight"]]
