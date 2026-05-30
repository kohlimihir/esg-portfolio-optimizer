from __future__ import annotations
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ..utils.config import Paths
from ..utils.logging import logger

app = FastAPI(title="ESG Scoring API", version="0.1.0")

_scores_cache: pd.DataFrame | None = None


def _load_scores() -> pd.DataFrame:
    global _scores_cache
    if _scores_cache is None:
        path = Paths.from_config().features / "esg_scores.parquet"
        if not path.exists():
            raise FileNotFoundError("Run the pipeline before serving the API.")
        _scores_cache = pd.read_parquet(path)
    return _scores_cache


class ScoreResponse(BaseModel):
    ticker: str
    sector: str | None
    e_score: float
    s_score: float
    g_score: float
    esg_score: float
    sector_percentile: float


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/score/{ticker}", response_model=ScoreResponse)
def score(ticker: str) -> ScoreResponse:
    df = _load_scores()
    ticker = ticker.upper()
    row = df[df["ticker"] == ticker]
    if row.empty:
        raise HTTPException(404, f"Ticker {ticker} not found")
    r = row.iloc[0]
    sector_pctile = (
        df[df["sector"] == r["sector"]]["esg_score"].rank(pct=True).loc[row.index[0]]
    )
    return ScoreResponse(
        ticker=ticker,
        sector=r.get("sector"),
        e_score=float(r["e_score"]),
        s_score=float(r["s_score"]),
        g_score=float(r["g_score"]),
        esg_score=float(r["esg_score"]),
        sector_percentile=float(sector_pctile),
    )


@app.get("/leaderboard")
def leaderboard(top_n: int = 25, sector: str | None = None) -> list[dict]:
    df = _load_scores()
    if sector:
        df = df[df["sector"] == sector]
    return (
        df.sort_values("esg_score", ascending=False)
        .head(top_n)[["ticker", "sector", "esg_score"]]
        .to_dict(orient="records")
    )
