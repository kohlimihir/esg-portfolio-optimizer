from __future__ import annotations
import pandas as pd
import numpy as np
from pathlib import Path
from ..utils.config import Paths
from ..utils.logging import logger


def _zscore_by_group(s: pd.Series, group: pd.Series) -> pd.Series:
    return s.groupby(group).transform(lambda x: (x - x.mean()) / (x.std(ddof=0) + 1e-9))


def build_environmental(universe: pd.DataFrame, epa: pd.DataFrame | None,
                        fundamentals: pd.DataFrame, edgar_meta: pd.DataFrame) -> pd.DataFrame:
    df = universe[["ticker", "sector"]].copy()
    df = df.merge(fundamentals[["ticker", "totalRevenue"]], on="ticker", how="left")
    df = df.merge(edgar_meta[["ticker", "climate"]].rename(columns={"climate": "climate_mentions"}),
                  on="ticker", how="left")
    
    if epa is not None and "GHG QUANTITY (METRIC TONS CO2e)" in epa.columns:
        # crude name match; in practice you'd join on a parent-company crosswalk
        emissions = epa.groupby("PARENT COMPANIES")["GHG QUANTITY (METRIC TONS CO2e)"].sum()
        df["emissions"] = df["ticker"].map({})  # placeholder; needs crosswalk
    
    df["emissions"] = df.get("emissions", np.nan)
    df["carbon_intensity"] = df["emissions"] / df["totalRevenue"]
    df["climate_mentions"] = df["climate_mentions"].fillna(0)
    df["e_climate_z"] = _zscore_by_group(df["climate_mentions"], df["sector"])
    df["e_intensity_z"] = _zscore_by_group(df["carbon_intensity"].fillna(df["carbon_intensity"].median()), df["sector"])
    
    return df[["ticker", "sector", "emissions", "carbon_intensity",
               "climate_mentions", "e_climate_z", "e_intensity_z"]]


def build_social(universe: pd.DataFrame, gdelt: pd.DataFrame | None,
                 edgar_meta: pd.DataFrame) -> pd.DataFrame:
    df = universe[["ticker", "sector"]].copy()
    df = df.merge(edgar_meta[["ticker", "labor"]].rename(columns={"labor": "labor_mentions"}),
                  on="ticker", how="left")
    df["labor_mentions"] = df["labor_mentions"].fillna(0)
    
    if gdelt is not None and not gdelt.empty:
        social = gdelt[gdelt["theme"].isin(["LABOR_DISPUTE"])].groupby("ticker").size()
        df["labor_controversy_count"] = df["ticker"].map(social).fillna(0)
    else:
        df["labor_controversy_count"] = 0
    
    df["s_disclosure_z"] = _zscore_by_group(df["labor_mentions"], df["sector"])
    df["s_controversy_z"] = _zscore_by_group(df["labor_controversy_count"], df["sector"])
    
    return df[["ticker", "sector", "labor_mentions",
               "labor_controversy_count", "s_disclosure_z", "s_controversy_z"]]


def build_governance(universe: pd.DataFrame, fundamentals: pd.DataFrame,
                     edgar_meta: pd.DataFrame, gdelt: pd.DataFrame | None) -> pd.DataFrame:
    df = universe[["ticker", "sector"]].copy()
    df = df.merge(edgar_meta[["ticker", "governance"]].rename(columns={"governance": "gov_mentions"}),
                  on="ticker", how="left")
    df = df.merge(fundamentals[["ticker", "debtToEquity"]], on="ticker", how="left")
    df["gov_mentions"] = df["gov_mentions"].fillna(0)
    
    if gdelt is not None and not gdelt.empty:
        corr = gdelt[gdelt["theme"].isin(["CORRUPTION"])].groupby("ticker").size()
        df["corruption_news"] = df["ticker"].map(corr).fillna(0)
    else:
        df["corruption_news"] = 0
    
    df["g_disclosure_z"] = _zscore_by_group(df["gov_mentions"], df["sector"])
    df["g_leverage_z"] = _zscore_by_group(df["debtToEquity"].fillna(df["debtToEquity"].median()), df["sector"])
    df["g_corruption_z"] = _zscore_by_group(df["corruption_news"], df["sector"])
    
    return df[["ticker", "sector", "gov_mentions", "corruption_news",
               "g_disclosure_z", "g_leverage_z", "g_corruption_z"]]


def build_feature_store() -> pd.DataFrame:
    paths = Paths.from_config()
    universe = pd.read_parquet(paths.raw / "sp500_constituents.parquet")
    fundamentals = pd.read_parquet(paths.raw / "yahoo_fundamentals.parquet")
    edgar_meta = pd.read_parquet(paths.raw / "edgar_metadata.parquet")
    gdelt = pd.read_parquet(paths.raw / "gdelt_articles.parquet") if (paths.raw / "gdelt_articles.parquet").exists() else None
    epa = pd.read_parquet(paths.raw / "epa_ghg.parquet") if (paths.raw / "epa_ghg.parquet").exists() else None
    
    e = build_environmental(universe, epa, fundamentals, edgar_meta)
    s = build_social(universe, gdelt, edgar_meta)
    g = build_governance(universe, fundamentals, edgar_meta, gdelt)
    
    feat = e.merge(s.drop(columns=["sector"]), on="ticker").merge(g.drop(columns=["sector"]), on="ticker")
    feat.to_parquet(paths.features / "feature_store.parquet", index=False)
    logger.success(f"Feature store built: {feat.shape}")
    return feat
