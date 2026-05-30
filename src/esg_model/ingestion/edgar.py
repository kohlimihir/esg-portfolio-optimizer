from __future__ import annotations
import re
import time
from pathlib import Path
import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from ..utils.logging import logger
from ..utils.config import Paths, load_yaml

SEC_HEADERS = {"User-Agent": load_yaml("data_sources.yaml")["edgar"]["user_agent"]}
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
TICKER_CIK_URL = "https://www.sec.gov/files/company_tickers.json"


def _cik_map() -> dict[str, str]:
    r = requests.get(TICKER_CIK_URL, headers=SEC_HEADERS, timeout=20)
    r.raise_for_status()
    data = r.json()
    return {row["ticker"]: str(row["cik_str"]).zfill(10) for row in data.values()}


def fetch_recent_10k(ticker: str, cik: str) -> dict | None:
    url = SUBMISSIONS_URL.format(cik=cik)
    r = requests.get(url, headers=SEC_HEADERS, timeout=20)
    if r.status_code != 200:
        return None
    recent = r.json().get("filings", {}).get("recent", {})
    if not recent:
        return None
    df = pd.DataFrame(recent)
    df = df[df["form"] == "10-K"].sort_values("filingDate", ascending=False)
    if df.empty:
        return None
    row = df.iloc[0]
    accession = row["accessionNumber"].replace("-", "")
    doc_url = (
        f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/"
        f"{row['primaryDocument']}"
    )
    return {
        "ticker": ticker, "cik": cik, "form": "10-K",
        "filed": row["filingDate"], "url": doc_url,
    }


def extract_text(url: str, retries: int = 3) -> str:
    """Extract text from SEC filing with retry logic."""
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=SEC_HEADERS, timeout=60)
            if r.status_code != 200:
                return ""
            soup = BeautifulSoup(r.content, "lxml")
            for tag in soup(["script", "style", "table"]):
                tag.decompose()
            text = soup.get_text(" ")
            text = re.sub(r"\s+", " ", text)
            return text
        except (requests.exceptions.ConnectionError, 
                requests.exceptions.Timeout,
                ConnectionResetError) as e:
            if attempt < retries - 1:
                wait_time = (attempt + 1) * 2  # 2, 4, 6 seconds
                logger.warning(f"Connection error, retrying in {wait_time}s: {e}")
                import time
                time.sleep(wait_time)
            else:
                logger.error(f"Failed to fetch {url} after {retries} attempts")
                return ""
    return ""


ESG_SECTION_PATTERNS = {
    "climate": r"(climate change|carbon emissions|greenhouse gas|renewable energy)",
    "labor": r"(human capital|employee|labor practices|diversity|equity|inclusion)",
    "governance": r"(board of directors|audit committee|executive compensation|insider)",
}


def section_mentions(text: str) -> dict[str, int]:
    text_l = text.lower()
    return {k: len(re.findall(p, text_l)) for k, p in ESG_SECTION_PATTERNS.items()}


def ingest_edgar(tickers: list[str], limit_chars: int = 500_000) -> None:
    paths = Paths.from_config()
    
    # Check if we have partial results and resume from there
    metadata_path = paths.raw / "edgar_metadata.parquet"
    texts_path = paths.raw / "edgar_texts.parquet"
    
    existing_tickers = set()
    if metadata_path.exists():
        existing_df = pd.read_parquet(metadata_path)
        existing_tickers = set(existing_df['ticker'].tolist())
        logger.info(f"Found {len(existing_tickers)} existing EDGAR filings, resuming...")
        rows = existing_df.to_dict('records')
        texts_df = pd.read_parquet(texts_path)
        texts = texts_df.to_dict('records')
    else:
        rows, texts = [], []
    
    cik_map = _cik_map()
    
    for tk in tqdm(tickers, desc="EDGAR ingestion"):
        # Skip if already processed
        if tk in existing_tickers:
            continue
            
        cik = cik_map.get(tk.replace("-", "."))
        if not cik:
            continue
        meta = fetch_recent_10k(tk, cik)
        if not meta:
            continue
        text = extract_text(meta["url"])[:limit_chars]
        if not text:  # Skip if extraction failed
            continue
        mentions = section_mentions(text)
        rows.append({**meta, **mentions, "text_length": len(text)})
        texts.append({"ticker": tk, "filed": meta["filed"], "text": text})
        
        # Save progress every 50 tickers
        if len(rows) % 50 == 0:
            pd.DataFrame(rows).to_parquet(metadata_path, index=False)
            pd.DataFrame(texts).to_parquet(texts_path, index=False)
    
    # Final save
    pd.DataFrame(rows).to_parquet(metadata_path, index=False)
    pd.DataFrame(texts).to_parquet(texts_path, index=False)
    logger.success(f"EDGAR ingestion complete ({len(rows)} filings)")
