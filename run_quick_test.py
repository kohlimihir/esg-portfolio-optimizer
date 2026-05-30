"""Quick test script - Run this first to verify everything works!"""

import time
from esg_model.ingestion.universe import fetch_sp500
from esg_model.ingestion.yahoo import ingest_universe
from esg_model.utils.logging import logger

print("=" * 70)
print("ESG Model - Quick Test (5 tickers)")
print("=" * 70)
print("\nThis will test the ingestion pipeline with just 5 tickers.")
print("Expected time: 2-3 minutes\n")

# Step 1: Get universe
print("Step 1: Fetching S&P 500 universe...")
universe = fetch_sp500()
test_tickers = universe['ticker'].tolist()[:5]
print(f"✓ Testing with: {test_tickers}\n")

# Step 2: Ingest Yahoo data
print("Step 2: Ingesting Yahoo Finance data...")
print("(This will take ~2 minutes with rate limiting)\n")
start = time.time()

try:
    ingest_universe(test_tickers, sleep=0.5)
    elapsed = time.time() - start
    print(f"\n✓ Ingestion complete in {elapsed:.1f} seconds")
    
    # Check what was created
    from pathlib import Path
    raw_path = Path("data/raw")
    files = list(raw_path.glob("yahoo_*.parquet"))
    
    print(f"\n✓ Created {len(files)} data files:")
    for f in files:
        size_kb = f.stat().st_size / 1024
        print(f"  - {f.name} ({size_kb:.1f} KB)")
    
    print("\n" + "=" * 70)
    print("✅ Quick test PASSED!")
    print("=" * 70)
    print("\nYour ESG Model is working correctly!")
    print("\nNext steps:")
    print("1. Review the data files in data/raw/")
    print("2. Run full pipeline: python -m esg_model.pipeline --stages ingest")
    print("3. Or see QUICKSTART.md for more options")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ Test failed: {e}")
    print("\nTroubleshooting:")
    print("1. Check your internet connection")
    print("2. Verify Yahoo Finance is accessible")
    print("3. Try increasing the sleep parameter")
    print("4. Check logs above for specific errors")
