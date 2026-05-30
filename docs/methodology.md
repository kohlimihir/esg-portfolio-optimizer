# ESG Scoring Methodology

## Overview

This model generates ESG scores for US-listed equities by combining quantitative metrics, regulatory disclosures, and news sentiment across three pillars: Environmental (E), Social (S), and Governance (G).

## Data Sources

### 1. Yahoo Finance
- **Sustainability scores**: Sustainalytics-derived ESG risk scores
- **Fundamentals**: Market cap, P/E, ROE, debt-to-equity
- **Price history**: 10 years of daily adjusted close prices

### 2. SEC EDGAR
- **10-K filings**: Annual reports with ESG-related disclosures
- **Text analysis**: Keyword frequency for climate, labor, governance topics

### 3. GDELT
- **News coverage**: Global news articles mentioning company + ESG themes
- **Controversy detection**: Labor disputes, corruption, emissions violations

### 4. EPA
- **Greenhouse gas emissions**: Facility-level CO2e data
- **Carbon intensity**: Emissions normalized by revenue

## Feature Engineering

### Environmental Pillar (E)
- Climate disclosure mentions in 10-K
- Carbon intensity (emissions / revenue)
- Sector-normalized z-scores

### Social Pillar (S)
- Labor practice disclosures in 10-K
- GDELT labor controversy count
- Sector-normalized z-scores

### Governance Pillar (G)
- Board/audit committee mentions in 10-K
- Debt-to-equity ratio
- GDELT corruption news count
- Sector-normalized z-scores

## Modeling Approach

### Pillar Models
- **Algorithm**: XGBoost regression
- **Target**: Yahoo Sustainalytics E/S/G scores
- **Training**: 80/20 train/validation split
- **Evaluation**: MAE, Spearman rank correlation

### Composite Score
- **Weighted average**: E (40%), S (30%), G (30%)
- **Optional learned blend**: Ridge regression on controversy target

## Portfolio Construction

### Universe
- S&P 500 constituents

### Strategy
- **Selection**: Top quintile (20%) by ESG score
- **Weighting**: Sector-neutral equal weight
- **Rebalance**: Quarterly
- **Constraints**: 5% max single-stock weight

### Backtesting
- **Period**: 2015-2024
- **Benchmark**: SPY (S&P 500 ETF)
- **Costs**: 10 bps transaction cost
- **Metrics**: CAGR, Sharpe, Sortino, max drawdown, information ratio

## Limitations & Future Work

1. **Point-in-time bias**: Current S&P 500 only; needs historical constituents
2. **Label sparsity**: Yahoo ESG scores missing for many tickers
3. **EPA crosswalk**: Facility-to-ticker mapping is placeholder
4. **NLP integration**: FinBERT/ESG-BERT ready but not yet in pipeline
5. **Alternative data**: Could add Glassdoor reviews, patent filings, supply chain data

## References

- Sustainalytics ESG Risk Ratings
- SEC EDGAR API Documentation
- GDELT Project Documentation
- EPA Greenhouse Gas Reporting Program
