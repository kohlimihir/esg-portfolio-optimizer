# ESG Model — Scoring & Portfolio Integration

A production-ready ESG scoring model for US-listed equities with end-to-end pipeline from data ingestion to portfolio backtesting.

## Architecture

```
esg-model/
├── configs/                    # Configuration files
│   ├── data_sources.yaml      # Data source endpoints & storage paths
│   ├── model_config.yaml      # Model hyperparameters & training config
│   └── portfolio_config.yaml  # Portfolio construction parameters
├── src/esg_model/
│   ├── ingestion/             # Data collection modules
│   │   ├── universe.py        # S&P 500 constituents from Wikipedia
│   │   ├── yahoo.py           # Yahoo Finance (prices, fundamentals, ESG)
│   │   ├── edgar.py           # SEC EDGAR 10-K filings
│   │   ├── gdelt.py           # GDELT news & controversy data
│   │   └── epa.py             # EPA greenhouse gas emissions
│   ├── processing/            # Feature engineering
│   │   ├── text.py            # Text cleaning & chunking
│   │   ├── nlp_models.py      # FinBERT & ESG-BERT inference
│   │   └── features.py        # E/S/G pillar feature construction
│   ├── models/                # Machine learning
│   │   ├── base.py            # Training utilities & MLflow tracking
│   │   ├── pillars.py         # Individual E/S/G pillar models
│   │   └── composite.py       # Composite ESG score aggregation
│   ├── portfolio/             # Portfolio construction & backtesting
│   │   ├── constructor.py     # Sector-neutral weight optimization
│   │   └── backtester.py      # Quarterly rebalance backtest
│   ├── api/                   # FastAPI REST API
│   │   └── main.py            # /score/{ticker} & /leaderboard endpoints
│   ├── dashboard/             # Streamlit visualization
│   │   └── app.py             # Interactive ESG dashboard
│   ├── utils/                 # Shared utilities
│   │   ├── config.py          # YAML config loader
│   │   ├── logging.py         # Loguru setup
│   │   └── io.py              # Parquet I/O helpers
│   └── pipeline.py            # End-to-end orchestration
├── tests/                     # Unit tests
├── docker/                    # Dockerfiles for API & dashboard
└── data/                      # Data storage (created at runtime)
    ├── raw/                   # Ingested data
    ├── processed/             # Cleaned data
    └── features/              # Feature store & scores
```

## Quick Start

### Installation

```bash
pip install -e ".[dev]"
```

### Run the Pipeline

```bash
# Full pipeline (ingestion → features → training → scoring → backtest)
python -m esg_model.pipeline

# Run specific stages
python -m esg_model.pipeline --stages ingest features
```

### Serve the API

```bash
uvicorn esg_model.api.main:app --reload
```

Visit `http://localhost:8000/docs` for interactive API documentation.

### Launch Dashboard

```bash
streamlit run src/esg_model/dashboard/app.py
```

## Data Flow

1. **Ingestion** → Collect S&P 500 universe, Yahoo Finance data, SEC filings, GDELT news, EPA emissions
2. **Processing** → Extract ESG-relevant features from text, fundamentals, and controversy data
3. **Training** → Train XGBoost models for E/S/G pillars with MLflow tracking
4. **Scoring** → Generate composite ESG scores for all tickers
5. **Portfolio** → Construct sector-neutral top-quintile portfolio & backtest
6. **API/Dashboard** → Serve scores via REST API and interactive dashboard

## Key Features

- **Multi-source ingestion**: Yahoo Finance, SEC EDGAR, GDELT, EPA
- **NLP-powered**: FinBERT sentiment & ESG-BERT classification (ready to integrate)
- **Sector-neutral scoring**: Z-score normalization within GICS sectors
- **MLflow tracking**: Experiment tracking for all model training runs
- **Production-ready API**: FastAPI with health checks & leaderboard endpoint
- **Interactive dashboard**: Streamlit app with score lookup, peer comparison, backtest viz
- **Docker support**: Containerized API & dashboard deployments

## Configuration

All configuration is centralized in `configs/`:

- `data_sources.yaml`: Data endpoints, user agents, storage paths
- `model_config.yaml`: Model hyperparameters, training splits, MLflow settings
- `portfolio_config.yaml`: Rebalance frequency, sector neutrality, transaction costs

## Testing

```bash
pytest tests -v --cov=esg_model
```

## Docker Deployment

```bash
# Build & run API
docker build -f docker/Dockerfile.api -t esg-api .
docker run -p 8000:8000 esg-api

# Build & run dashboard
docker build -f docker/Dockerfile.dashboard -t esg-dashboard .
docker run -p 8501:8501 esg-dashboard
```

## Known Limitations

1. **EPA → ticker crosswalk**: Placeholder implementation; needs fuzzy matching on company names
2. **GDELT name matching**: False positives for short company names; add sector keywords
3. **Sparse Yahoo ESG labels**: Supplement with Kaggle ESG datasets for training
4. **NLP models**: FinBERT/ESG-BERT wired but not yet integrated into feature pipeline
5. **Survivorship bias**: Uses current S&P 500 only; needs historical constituent data

Each of these is a focused 1-2 day task with clear implementation path.

## License

MIT
