from __future__ import annotations
import pandas as pd
import numpy as np
from ..utils.config import Paths, load_yaml
from ..utils.logging import logger


def _quarterly_rebalance_dates(prices: pd.DataFrame) -> pd.DatetimeIndex:
    return prices.index.to_series().resample("Q").last().dropna().index


def _annual_return(returns: pd.Series) -> float:
    """Calculate annualized return (CAGR)."""
    total_return = (1 + returns).prod()
    years = len(returns) / 252
    return float((total_return ** (1 / years)) - 1) if years > 0 else 0.0


def _sharpe_ratio(returns: pd.Series, risk_free: float = 0.0) -> float:
    """Calculate Sharpe ratio."""
    excess = returns - risk_free / 252
    if excess.std() == 0:
        return 0.0
    return float(excess.mean() / excess.std() * np.sqrt(252))


def _sortino_ratio(returns: pd.Series, risk_free: float = 0.0) -> float:
    """Calculate Sortino ratio (downside deviation)."""
    excess = returns - risk_free / 252
    downside = excess[excess < 0]
    if len(downside) == 0 or downside.std() == 0:
        return 0.0
    return float(excess.mean() / downside.std() * np.sqrt(252))


def _max_drawdown(returns: pd.Series) -> float:
    """Calculate maximum drawdown."""
    cum_returns = (1 + returns).cumprod()
    running_max = cum_returns.expanding().max()
    drawdown = (cum_returns - running_max) / running_max
    return float(drawdown.min())


def backtest(weights: pd.DataFrame, prices_long: pd.DataFrame,
             benchmark_ticker: str = "SPY") -> dict:
    cfg = load_yaml("portfolio_config.yaml")
    cost = cfg["transaction_cost_bps"] / 10_000
    
    prices = prices_long.pivot(index="date", columns="ticker", values="close").sort_index()
    prices.index = pd.to_datetime(prices.index)
    prices = prices.loc[cfg["start"]:cfg["end"]]
    
    if benchmark_ticker not in prices.columns:
        import yfinance as yf
        bench = yf.download(benchmark_ticker, start=cfg["start"], end=cfg["end"],
                            auto_adjust=True, progress=False)["Close"]
        bench = bench.reindex(prices.index).ffill()
    else:
        bench = prices[benchmark_ticker]
    
    rets = prices.pct_change().fillna(0)
    rebal_dates = _quarterly_rebalance_dates(prices)
    
    w_target = weights.set_index("ticker")["weight"]
    w_target = w_target.reindex(prices.columns).fillna(0)
    w_current = pd.Series(0.0, index=prices.columns)
    portfolio_ret = pd.Series(0.0, index=prices.index)
    
    for date in prices.index:
        if date in rebal_dates:
            turnover = (w_target - w_current).abs().sum()
            portfolio_ret.loc[date] -= cost * turnover
            w_current = w_target.copy()
        
        day_ret = (w_current * rets.loc[date]).sum()
        portfolio_ret.loc[date] += day_ret
        
        # drift weights
        w_current = w_current * (1 + rets.loc[date])
        s = w_current.sum()
        if s > 0:
            w_current /= s
    
    bench_ret = bench.pct_change().fillna(0)
    
    metrics = {
        "cagr": _annual_return(portfolio_ret),
        "sharpe": _sharpe_ratio(portfolio_ret),
        "sortino": _sortino_ratio(portfolio_ret),
        "max_drawdown": _max_drawdown(portfolio_ret),
        "bench_cagr": _annual_return(bench_ret),
        "bench_sharpe": _sharpe_ratio(bench_ret),
        "tracking_error": float((portfolio_ret - bench_ret).std() * np.sqrt(252)),
        "information_ratio": float(
            (portfolio_ret.mean() - bench_ret.mean())
            / ((portfolio_ret - bench_ret).std() + 1e-9) * np.sqrt(252)
        ),
    }
    
    logger.info(f"Backtest metrics: {metrics}")
    paths = Paths.from_config()
    out = pd.DataFrame({"portfolio": portfolio_ret, "benchmark": bench_ret})
    out.to_parquet(paths.features / "backtest_returns.parquet")
    return metrics
