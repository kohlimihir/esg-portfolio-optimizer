from __future__ import annotations
import io
import pandas as pd
import requests
from ..utils.logging import logger
from ..utils.config import Paths, load_yaml


def ingest_epa() -> pd.DataFrame:
    cfg = load_yaml("data_sources.yaml")["epa"]
    paths = Paths.from_config()
    
    logger.info("Downloading EPA GHG data")
    r = requests.get(cfg["ghg_url"], timeout=120)
    r.raise_for_status()
    
    xls = pd.ExcelFile(io.BytesIO(r.content))
    # Sheet names vary by year; pick the direct emitters sheet
    sheet = next((s for s in xls.sheet_names if "Direct Emitters" in s), xls.sheet_names[0])
    df = pd.read_excel(xls, sheet_name=sheet, skiprows=3)
    df.columns = [str(c).strip() for c in df.columns]
    
    out_path = paths.raw / "epa_ghg.parquet"
    df.to_parquet(out_path, index=False)
    logger.success(f"EPA data saved to {out_path}")
    return df
