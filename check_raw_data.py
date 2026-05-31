import pandas as pd

files = {
    'sp500_constituents.parquet': 'S&P 500 company list',
    'yahoo_fundamentals.parquet': 'Yahoo financial metrics',
    'yahoo_prices.parquet': 'Stock price history',
    'edgar_metadata.parquet': 'SEC filing metadata',
    'edgar_texts.parquet': 'SEC filing full text',
    'gdelt_articles.parquet': 'News articles',
    'epa_ghg.parquet': 'EPA emissions data'
}

print("="*70)
print("DATA/RAW PARQUET FILES")
print("="*70)

for i, (filename, description) in enumerate(files.items(), 1):
    df = pd.read_parquet(f'data/raw/{filename}')
    print(f"\n{i}. {filename}")
    print(f"   Description: {description}")
    print(f"   Rows: {len(df):,}")
    print(f"   Columns ({len(df.columns)}): {', '.join(df.columns[:8])}")
    if len(df.columns) > 8:
        print(f"                 ... and {len(df.columns)-8} more")
    print(f"   Size: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")

print("\n" + "="*70)
print(f"TOTAL: {len(files)} files")
print("="*70)
