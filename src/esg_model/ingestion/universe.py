import pandas as pd
from pathlib import Path
from ..utils.logging import logger
from ..utils.config import Paths

SP500_WIKI = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"


def fetch_sp500() -> pd.DataFrame:
    """Pulls current S&P 500 constituents from Wikipedia."""
    paths = Paths.from_config()
    cache = paths.raw / "sp500_constituents.parquet"
    
    if cache.exists():
        logger.info(f"Loading cached S&P 500 from {cache}")
        return pd.read_parquet(cache)
    
    logger.info("Fetching S&P 500 constituents from Wikipedia")
    # Add User-Agent header to avoid 403 Forbidden
    tables = pd.read_html(
        SP500_WIKI,
        storage_options={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    )
    df = tables[0].rename(columns={
        "Symbol": "ticker",
        "Security": "name",
        "GICS Sector": "sector",
        "GICS Sub-Industry": "industry",
    })
    df["ticker"] = df["ticker"].str.replace(".", "-", regex=False)
    df = df[["ticker", "name", "sector", "industry"]]
    df.to_parquet(cache, index=False)
    return df
