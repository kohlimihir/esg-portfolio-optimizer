from __future__ import annotations
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
from ..utils.config import Paths

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

tab1, tab2, tab3, tab4 = st.tabs(["Score Lookup", "Peer Comparison", "Backtest", "Methodology"])

scores = load_scores()

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
        sub = scores[scores["sector"] == sector].sort_values("esg_score", ascending=False)
        fig = px.bar(sub, x="ticker", y="esg_score", title=f"{sector} ESG Ranking")
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    bt = load_backtest()
    if bt.empty:
        st.info("Run the backtest to populate this tab.")
    else:
        cum = (1 + bt).cumprod()
        fig = px.line(cum, title="Cumulative Returns: ESG Portfolio vs Benchmark")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(bt.describe())

with tab4:
    methodology_path = Path(__file__).resolve().parents[3] / "docs" / "methodology.md"
    st.markdown(
        methodology_path.read_text() if methodology_path.exists()
        else "Methodology doc not yet written."
    )
