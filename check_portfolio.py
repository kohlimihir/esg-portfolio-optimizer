import pandas as pd
from src.esg_model.portfolio.constructor import build_target_weights

scores = pd.read_parquet('data/features/esg_scores.parquet')
weights = build_target_weights(scores)

print(f"Portfolio has {len(weights)} stocks")
print(f"\nBy sector:")
print(weights.groupby('sector').size().sort_values(ascending=False))
print(f"\nTotal weight: {weights['weight'].sum():.4f}")
print(f"\nTop 10 holdings:")
print(weights.nlargest(10, 'weight')[['ticker', 'sector', 'esg_score', 'weight']])
print(f"\nWeight range: {weights['weight'].min():.4f} to {weights['weight'].max():.4f}")
