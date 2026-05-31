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
    
    # Handle xlsb format (binary Excel)
    try:
        # Try reading as xlsb (requires pyxlsb)
        xls = pd.ExcelFile(io.BytesIO(r.content), engine='pyxlsb')
    except Exception:
        # Fallback to openpyxl for xlsx
        xls = pd.ExcelFile(io.BytesIO(r.content))
    
    # Sheet names vary by year; look for relevant sheet
    # Parent company file typically has sheets like "Parent Companies" or similar
    sheet = None
    for s in xls.sheet_names:
        if any(keyword in s.lower() for keyword in ['parent', 'company', 'direct', 'emitter']):
            sheet = s
            break
    if sheet is None:
        sheet = xls.sheet_names[0]
    
    logger.info(f"Reading sheet: {sheet}")
    df = pd.read_excel(xls, sheet_name=sheet, engine='pyxlsb' if cfg["ghg_url"].endswith('.xlsb') else None)
    
    # Clean column names
    df.columns = [str(c).strip() for c in df.columns]
    
    out_path = paths.raw / "epa_ghg.parquet"
    df.to_parquet(out_path, index=False)
    logger.success(f"EPA data saved to {out_path} ({len(df)} rows)")
    return df
