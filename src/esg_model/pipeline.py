"""End-to-end orchestration. Run as: python -m esg_model.pipeline"""

from __future__ import annotations
import argparse
from .ingestion.universe import fetch_sp500
from .ingestion.yahoo import ingest_universe
from .ingestion.edgar import ingest_edgar
from .ingestion.gdelt import ingest_gdelt
from .ingestion.epa import ingest_epa
from .processing.features import build_feature_store
from .models.pillars import train_all_pillars
from .models.composite import build_composite_scores
from .portfolio.constructor import build_target_weights
from .portfolio.backtester import backtest
from .utils.logging import logger
from .utils.config import Paths
import pandas as pd


def run(stages: list[str]) -> None:
    universe = fetch_sp500()
    tickers = universe["ticker"].tolist()
    
    if "ingest" in stages:
        ingest_universe(tickers)
        ingest_edgar(tickers)
        ingest_gdelt(universe[["ticker", "name"]], "2023-01-01", "2024-12-31")
        try:
            ingest_epa()
        except Exception as e:
            logger.warning(f"EPA ingestion skipped: {e}")
    
    if "features" in stages:
        build_feature_store()
    
    if "train" in stages:
        train_all_pillars()
    
    if "score" in stages:
        build_composite_scores()
    
    if "backtest" in stages:
        paths = Paths.from_config()
        scores = pd.read_parquet(paths.features / "esg_scores.parquet")
        weights = build_target_weights(scores)
        prices = pd.read_parquet(paths.raw / "yahoo_prices.parquet")
        metrics = backtest(weights, prices)
        logger.success(f"Backtest done: {metrics}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--stages", nargs="+",
                   default=["ingest", "features", "train", "score", "backtest"])
    args = p.parse_args()
    run(args.stages)
