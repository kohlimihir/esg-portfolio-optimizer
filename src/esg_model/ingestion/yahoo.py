from __future__ import annotations
import time
import logging
import contextlib
import io
from pathlib import Path
import pandas as pd
import yfinance as yf
from tqdm import tqdm
from ..utils.logging import logger
from ..utils.config import Paths

# Silence yfinance's internal logger (the source of "HTTP Error 404" prints)
logging.getLogger("yfinance").setLevel(logging.CRITICAL)


@contextlib.contextmanager
def _silence_stderr():
    """Yahoo's 404s are printed to stderr by yfinance internals."""
    import sys
    old = sys.stderr
    sys.stderr = io.StringIO()
    try:
        yield
    finally:
        sys.stderr = old


def _safe(fn, default=None, retries: int = 2, backoff: float = 0.5):
    last_exc = None
    for attempt in range(retries + 1):
        try:
            with _silence_stderr():
                return fn()
        except Exception as e:
            last_exc = e
            if attempt < retries:
                time.sleep(backoff * (2 ** attempt))
    logger.debug(f"yfinance call failed after retries: {last_exc}")
    return default


# ---------------------------------------------------------------- sustainability
def fetch_sustainability(ticker: str) -> dict | None:
    """Yahoo exposes Sustainalytics-derived ESG risk scores."""
    t = yf.Ticker(ticker)
    sus = _safe(lambda: t.sustainability)
    if sus is None or (hasattr(sus, "empty") and sus.empty):
        return None
    try:
        s = sus.iloc[:, 0].to_dict()
    except Exception:
        return None
    out = {"ticker": ticker}
    for k in ("totalEsg", "environmentScore", "socialScore", "governanceScore",
              "esgPerformance", "highestControversy", "peerCount", "peerGroup"):
        out[k] = s.get(k)
    return out


# ---------------------------------------------------------------- fundamentals
def _from_fast_info(t: yf.Ticker) -> dict:
    """fast_info uses a different endpoint and rarely 404s."""
    fi = _safe(lambda: t.fast_info, {}) or {}
    out = {}
    # fast_info exposes attribute-style access
    for src, dst in [("market_cap", "marketCap"),
                     ("last_price", "lastPrice"),
                     ("shares", "sharesOutstanding"),
                     ("currency", "currency"),
                     ]:
        try:
            out[dst] = getattr(fi, src, None) or (fi.get(src) if hasattr(fi, "get") else None)
        except Exception:
            out[dst] = None
    return out


def _from_financials(t: yf.Ticker) -> dict:
    """Derive margins / revenue from statement tables when info module 404s."""
    out: dict = {}
    inc = _safe(lambda: t.financials)
    if inc is not None and not inc.empty:
        latest = inc.iloc[:, 0]
        rev = latest.get("Total Revenue")
        gp = latest.get("Gross Profit")
        op = latest.get("Operating Income")
        ni = latest.get("Net Income")
        out["totalRevenue"] = float(rev) if pd.notna(rev) else None
        if pd.notna(rev) and rev:
            if pd.notna(gp):
                out["grossMargins"] = float(gp) / float(rev)
            if pd.notna(op):
                out["operatingMargins"] = float(op) / float(rev)
            if pd.notna(ni):
                out["profitMargins"] = float(ni) / float(rev)
    
    bs = _safe(lambda: t.balance_sheet)
    if bs is not None and not bs.empty:
        latest = bs.iloc[:, 0]
        debt = latest.get("Total Debt")
        eq = latest.get("Stockholders Equity") or latest.get("Total Stockholder Equity")
        if pd.notna(debt) and pd.notna(eq) and eq:
            out["debtToEquity"] = float(debt) / float(eq) * 100
        if pd.notna(ni) if "ni" in locals() and pd.notna(ni) else False:
            if pd.notna(eq) and eq:
                out["returnOnEquity"] = float(ni) / float(eq)
    return out


def fetch_fundamentals(ticker: str) -> dict | None:
    t = yf.Ticker(ticker)
    # 1) Primary: get_info() — newer method, slightly more reliable than .info
    info = _safe(lambda: t.get_info(), {}) or {}
    # 2) Fallback: fast_info
    if not info:
        info = _from_fast_info(t)
    # 3) Augment with derived values from financial statements
    derived = _from_financials(t)
    for k, v in derived.items():
        info.setdefault(k, v)
    
    if not info:
        return None
    
    keys = [
        "marketCap", "enterpriseValue", "trailingPE", "forwardPE",
        "priceToBook", "profitMargins", "returnOnEquity", "debtToEquity",
        "totalRevenue", "grossMargins", "operatingMargins", "sector",
    ]
    row = {"ticker": ticker, **{k: info.get(k) for k in keys}}
    # Drop rows that are entirely empty besides the ticker
    if all(row[k] is None for k in keys):
        return None
    return row


# ---------------------------------------------------------------- prices
def fetch_prices(tickers: list[str], period: str = "10y",
                 batch_size: int = 50) -> pd.DataFrame:
    """Batched price download — single big call sometimes drops tickers silently."""
    logger.info(f"Downloading prices for {len(tickers)} tickers in batches of {batch_size}")
    frames: list[pd.DataFrame] = []
    
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i + batch_size]
        df = _safe(
            lambda b=batch: yf.download(
                b, period=period, auto_adjust=True, progress=False,
                group_by="ticker", threads=True,
            ),
            default=pd.DataFrame(),
        )
        if df is None or df.empty:
            continue
        
        # Single ticker -> flat columns; multiple -> MultiIndex
        if len(batch) == 1:
            tk = batch[0]
            if {"Close", "Volume"}.issubset(df.columns):
                sub = df[["Close", "Volume"]].reset_index()
                sub["ticker"] = tk
                frames.append(sub)
        else:
            for tk in batch:
                try:
                    sub = df[tk][["Close", "Volume"]].reset_index()
                    sub["ticker"] = tk
                    frames.append(sub)
                except (KeyError, ValueError):
                    continue
    
    if not frames:
        logger.warning("No price data returned for any ticker")
        return pd.DataFrame(columns=["date", "close", "volume", "ticker"])
    
    out = pd.concat(frames, ignore_index=True).rename(
        columns={"Date": "date", "Close": "close", "Volume": "volume"}
    )
    return out.dropna(subset=["close"])


# ---------------------------------------------------------------- orchestrator
def ingest_universe(tickers: list[str], sleep: float = 0.15) -> None:
    paths = Paths.from_config()
    sus_rows, fund_rows = [], []
    sus_fail, fund_fail = 0, 0
    
    for tk in tqdm(tickers, desc="Yahoo ingestion"):
        s = fetch_sustainability(tk)
        if s:
            sus_rows.append(s)
        else:
            sus_fail += 1
        
        f = fetch_fundamentals(tk)
        if f:
            fund_rows.append(f)
        else:
            fund_fail += 1
        
        time.sleep(sleep)
    
    logger.info(f"Sustainability: {len(sus_rows)} ok / {sus_fail} empty | "
                f"Fundamentals: {len(fund_rows)} ok / {fund_fail} empty")
    
    if sus_rows:
        pd.DataFrame(sus_rows).to_parquet(paths.raw / "yahoo_sustainability.parquet", index=False)
    if fund_rows:
        pd.DataFrame(fund_rows).to_parquet(paths.raw / "yahoo_fundamentals.parquet", index=False)
    
    prices = fetch_prices(tickers)
    if not prices.empty:
        prices.to_parquet(paths.raw / "yahoo_prices.parquet", index=False)
    
    logger.success("Yahoo ingestion complete")
