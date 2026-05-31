from __future__ import annotations
from pathlib import Path
import sys
import pandas as pd
import streamlit as st
import plotly.express as px

# Add project root to path for imports
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.esg_model.utils.config import Paths

st.set_page_config(page_title="ESG Model", layout="wide")

paths = Paths.from_config()
scores_path = paths.features / "esg_scores.parquet"
backtest_path = paths.features / "backtest_returns.parquet"


@st.cache_data
def load_scores() -> pd.DataFrame:
    return pd.read_parquet(scores_path) if scores_path.exists() else pd.DataFrame()


@st.cache_data
def load_backtest() -> pd.DataFrame:
    return pd.read_parquet(backtest_path) if backtest_path.exists() else pd.DataFrame()


st.title("ESG Scoring & Portfolio")

# Load data first
scores = load_scores()

# Add summary metrics at the top
if not scores.empty:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Companies", len(scores))
    col2.metric("Best ESG Score", f"{scores['esg_score'].min():.2f}")
    col3.metric("Avg ESG Score", f"{scores['esg_score'].mean():.2f}")
    col4.metric("Sectors Covered", scores['sector'].nunique())

tab1, tab2, tab3, tab4 = st.tabs(["Score Lookup", "Peer Comparison", "Backtest", "Methodology"])

with tab1:
    if scores.empty:
        st.warning("No scores available — run the pipeline first.")
    else:
        ticker = st.selectbox("Select ticker", sorted(scores["ticker"].unique()))
        row = scores[scores["ticker"] == ticker].iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("ESG", f"{row['esg_score']:.2f}")
        c2.metric("E", f"{row['e_score']:.2f}")
        c3.metric("S", f"{row['s_score']:.2f}")
        c4.metric("G", f"{row['g_score']:.2f}")
        st.write(f"**Sector:** {row['sector']}")

with tab2:
    if not scores.empty:
        sector = st.selectbox("Sector", sorted(scores["sector"].dropna().unique()))
        sub = scores[scores["sector"] == sector].sort_values("esg_score", ascending=True)  # Lower is better
        fig = px.bar(
            sub, 
            x="ticker", 
            y="esg_score", 
            title=f"{sector} ESG Ranking (Lower Score = Better ESG)",
            labels={'esg_score': 'ESG Risk Score', 'ticker': 'Company'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Show top 10 in table
        st.subheader(f"Top 10 ESG Companies in {sector}")
        top10 = sub.head(10)[['ticker', 'esg_score', 'e_score', 's_score', 'g_score']]
        st.dataframe(top10, hide_index=True)

with tab3:
    bt = load_backtest()
    if bt.empty:
        st.info("Run the backtest to populate this tab.")
    else:
        # Reset index to make date a column for plotting
        bt_plot = bt.reset_index()
        
        # Calculate cumulative returns
        cum = (1 + bt[['portfolio', 'benchmark']]).cumprod()
        cum_plot = cum.reset_index()
        
        # Plot cumulative returns
        fig = px.line(
            cum_plot, 
            x='date', 
            y=['portfolio', 'benchmark'],
            title="Cumulative Returns: ESG Portfolio vs S&P 500",
            labels={'value': 'Cumulative Return', 'variable': 'Strategy', 'date': 'Date'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Plot ESG score over time
        fig_esg = px.line(
            bt_plot,
            x='date',
            y='portfolio_esg',
            title="Portfolio ESG Score Over Time",
            labels={'portfolio_esg': 'Average ESG Score', 'date': 'Date'}
        )
        st.plotly_chart(fig_esg, use_container_width=True)
        
        # Show statistics
        st.subheader("Performance Statistics")
        stats = bt[['portfolio', 'benchmark']].describe()
        st.dataframe(stats)

with tab4:
    methodology_path = Path(__file__).resolve().parents[3] / "docs" / "methodology.md"
    st.markdown(
        methodology_path.read_text() if methodology_path.exists()
        else "Methodology doc not yet written."
    )
