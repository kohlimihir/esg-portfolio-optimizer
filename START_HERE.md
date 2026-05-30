# 🎯 START HERE - ESG Model Quick Guide

## ✅ Installation Complete!

Your ESG scoring model is installed and ready. All tests passed successfully.

## 🚀 Three Ways to Get Started

### 1️⃣ Quick Test (2 minutes) - **RECOMMENDED FIRST**

Test with just 5 tickers to verify everything works:

```bash
python run_quick_test.py
```

This will:
- Fetch 5 S&P 500 tickers
- Download their Yahoo Finance data
- Verify the pipeline works
- Show you what data was created

### 2️⃣ Full Pipeline (4-8 hours)

Run the complete ESG scoring pipeline:

```bash
# All stages at once
python -m esg_model.pipeline

# Or run stages individually
python -m esg_model.pipeline --stages ingest      # 3-5 hours
python -m esg_model.pipeline --stages features    # 5-10 min
python -m esg_model.pipeline --stages train       # 2-5 min
python -m esg_model.pipeline --stages score       # 1 min
python -m esg_model.pipeline --stages backtest    # 2-5 min
```

### 3️⃣ Launch Services

If you already have data/scores:

```bash
# API (Terminal 1)
uvicorn esg_model.api.main:app --reload
# Visit: http://localhost:8000/docs

# Dashboard (Terminal 2)
streamlit run src/esg_model/dashboard/app.py
# Visit: http://localhost:8501
```

## 📚 Documentation

| File | Purpose |
|------|---------|
| **START_HERE.md** | This file - quick start |
| **QUICKSTART.md** | Step-by-step usage guide |
| **README.md** | Complete project documentation |
| **docs/methodology.md** | ESG scoring methodology |

## 🧪 Test Script

- **`run_quick_test.py`** - Real data ingestion test with 5 tickers (~2 min)
- **`tests/`** - Unit tests for features and portfolio modules

## 📊 What You Have Now

```
✓ 503 S&P 500 tickers loaded
✓ 11 sectors identified  
✓ All modules working
✓ Configuration loaded
✓ Data directories created
✓ API structure ready
✓ Dashboard ready
✓ Tests passing
```

## 🎯 Recommended Path

```
1. Run: python run_quick_test.py          (2 min)
   → Verifies ingestion works

2. Review: data/raw/yahoo_*.parquet       (1 min)
   → Check what data looks like

3. Read: QUICKSTART.md                    (5 min)
   → Understand the full pipeline

4. Run: python -m esg_model.pipeline      (4-8 hours)
   → Generate ESG scores

5. Launch: uvicorn esg_model.api.main:app (instant)
   → Use the API

6. Launch: streamlit run ...              (instant)
   → Visualize results
```

## ⚡ Quick Commands

```bash
# Quick ingestion test (recommended first)
python run_quick_test.py

# Run full pipeline
python -m esg_model.pipeline

# Start API
uvicorn esg_model.api.main:app --reload

# Start dashboard
streamlit run src/esg_model/dashboard/app.py

# Run unit tests
pytest tests -v

# Lint code
ruff check src tests
```

## 🔍 What's Next?

After running the quick test, you can:

1. **Explore the data** in `data/raw/`
2. **Customize features** in `src/esg_model/processing/features.py`
3. **Tune models** in `configs/model_config.yaml`
4. **Adjust portfolio** in `configs/portfolio_config.yaml`
5. **Add data sources** in `src/esg_model/ingestion/`

## 💡 Pro Tips

- **Start small**: Always test with a few tickers first
- **Monitor logs**: Watch for rate limit warnings
- **Use caching**: Data is cached automatically
- **Check quality**: Inspect parquet files regularly
- **Iterate**: Modify and re-run as you learn

## 🆘 Need Help?

1. Review **QUICKSTART.md** for detailed instructions
2. Read **README.md** for architecture details
3. Check **docs/methodology.md** for ESG scoring approach
4. Check logs in the console for errors

## 🎉 You're Ready!

Your ESG Model is fully installed and tested. Start with:

```bash
python run_quick_test.py
```

Then explore the documentation and customize as needed.

**Happy modeling! 📊🚀**
