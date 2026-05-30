# ESG Model - Quick Start Guide

## ✅ Installation Complete!

Your ESG model is now installed and ready to use.

## 🚀 Next Steps

### 1. Test a Small Subset First

Before running the full pipeline (which can take hours), test with a small subset:

```bash
# Test with just 5 tickers
python -c "from esg_model.ingestion.universe import fetch_sp500; print(fetch_sp500().head())"
```

### 2. Run Individual Stages

You can run each stage independently:

```bash
# Stage 1: Fetch S&P 500 universe
python -c "from esg_model.ingestion.universe import fetch_sp500; fetch_sp500()"

# Stage 2: Ingest Yahoo data (slow - ~10 min for 500 tickers)
# python -c "from esg_model.ingestion.yahoo import ingest_universe; from esg_model.ingestion.universe import fetch_sp500; ingest_universe(fetch_sp500()['ticker'].tolist()[:10])"

# Stage 3: Build features
# python -c "from esg_model.processing.features import build_feature_store; build_feature_store()"
```

### 3. Run Full Pipeline

**⚠️ Warning**: This will take several hours and make many API calls!

```bash
python -m esg_model.pipeline
```

Or run specific stages:

```bash
# Just ingestion
python -m esg_model.pipeline --stages ingest

# Just feature engineering
python -m esg_model.pipeline --stages features

# Training only
python -m esg_model.pipeline --stages train

# Scoring only
python -m esg_model.pipeline --stages score

# Backtesting only
python -m esg_model.pipeline --stages backtest
```

### 4. Launch the API

Once you have scores generated:

```bash
uvicorn esg_model.api.main:app --reload
```

Then visit: `http://localhost:8000/docs`

### 5. Launch the Dashboard

```bash
streamlit run src/esg_model/dashboard/app.py
```

Then visit: `http://localhost:8501`

## 📊 Expected Data Flow

```
1. Universe (S&P 500) → data/raw/sp500_constituents.parquet
2. Yahoo Finance → data/raw/yahoo_*.parquet
3. EDGAR Filings → data/raw/edgar_*.parquet
4. GDELT News → data/raw/gdelt_articles.parquet
5. EPA Emissions → data/raw/epa_ghg.parquet
6. Features → data/features/feature_store.parquet
7. Models → models/pillar_*.joblib
8. Scores → data/features/esg_scores.parquet
9. Backtest → data/features/backtest_returns.parquet
```

## ⚡ Quick Commands

```bash
# Run tests
pytest tests -v

# Lint code
ruff check src tests

# Type check
mypy src --ignore-missing-imports

# Format code
ruff check --fix src tests
```

## 🐛 Troubleshooting

### Rate Limiting

If you hit rate limits:
- **Yahoo Finance**: Add `sleep` parameter in `ingest_universe()`
- **EDGAR**: Increase sleep time between requests
- **GDELT**: Reduce `maxrecords` parameter

### Missing Data

Some tickers may not have:
- Yahoo ESG scores (sparse coverage)
- EDGAR filings (recently listed companies)
- EPA emissions data (needs company name matching)

This is expected - the model handles missing data gracefully.

### Memory Issues

If you run out of memory:
- Process tickers in batches
- Reduce `history_period` in configs
- Limit EDGAR text to fewer characters

## 📝 Configuration

Edit these files to customize:
- `configs/data_sources.yaml` - Data endpoints & storage
- `configs/model_config.yaml` - Model hyperparameters
- `configs/portfolio_config.yaml` - Portfolio parameters

## 🎯 What to Expect

**First Run (Full Pipeline)**:
- **Time**: 4-8 hours depending on network speed
- **Data**: ~500 MB of raw data
- **API Calls**: ~2,500 to Yahoo, ~500 to EDGAR, ~10,000 to GDELT

**Subsequent Runs**:
- Much faster as data is cached
- Only new data is fetched

## 💡 Tips

1. **Start small**: Test with 10-20 tickers first
2. **Cache everything**: The pipeline caches aggressively
3. **Monitor logs**: Watch for rate limit warnings
4. **Check data quality**: Inspect parquet files in `data/raw/`
5. **Iterate on features**: Modify `processing/features.py` as needed

## 📚 Next Steps

1. Read `docs/methodology.md` for scoring details
2. Explore the API at `/docs` endpoint
3. Customize features in `src/esg_model/processing/features.py`
4. Tune models in `configs/model_config.yaml`
5. Adjust portfolio strategy in `configs/portfolio_config.yaml`

Happy modeling! 🚀
