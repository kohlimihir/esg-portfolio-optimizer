from __future__ import annotations
import time
import pandas as pd
import requests
from tqdm import tqdm
from ..utils.logging import logger
from ..utils.config import Paths, load_yaml


def query_gdelt(company: str, theme: str, start: str, end: str, maxrecords: int = 250) -> pd.DataFrame:
    cfg = load_yaml("data_sources.yaml")["gdelt"]
    params = {
        "query": f'"{company}" theme:{theme}',
        "mode": "ArtList",
        "format": "json",
        "startdatetime": start.replace("-", "") + "000000",
        "enddatetime": end.replace("-", "") + "235959",
        "maxrecords": maxrecords,
    }
    try:
        r = requests.get(cfg["base_url"], params=params, timeout=30)
        if r.status_code != 200:
            return pd.DataFrame()
        data = r.json().get("articles", [])
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        df["company"] = company
        df["theme"] = theme
        return df
    except Exception as e:
        logger.debug(f"GDELT query failed: {e}")
        return pd.DataFrame()


def ingest_gdelt(companies: pd.DataFrame, start: str, end: str) -> None:
    """companies: DataFrame with columns [ticker, name]."""
    paths = Paths.from_config()
    themes = load_yaml("data_sources.yaml")["gdelt"]["themes"]
    rows = []
    
    for _, row in tqdm(companies.iterrows(), total=len(companies), desc="GDELT"):
        for theme in themes:
            df = query_gdelt(row["name"], theme, start, end)
            if not df.empty:
                df["ticker"] = row["ticker"]
                rows.append(df[["ticker", "company", "theme", "url", "title", "seendate"]])
            time.sleep(0.3)
    
    if rows:
        out = pd.concat(rows, ignore_index=True)
        out.to_parquet(paths.raw / "gdelt_articles.parquet", index=False)
        logger.success(f"GDELT ingestion complete ({len(out)} articles)")
