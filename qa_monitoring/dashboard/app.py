"""
dashboard/app.py
----------------
Streamlit dashboard for the QA Monitoring and Alert System.

Sections:
  • Sidebar  – date-range & agent filters
  • KPI row  – Avg QA, Avg CSAT, Escalation %, Correlation
  • Charts   – QA distribution | CSAT vs QA | Escalation by issue
  • Tables   – Top performers | Low-performing agents

Run:
  cd qa_monitoring
  streamlit run dashboard/app.py
"""

import os
import sys
import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

# Allow imports from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.analyze_data import (
    load_data, agent_summary, issue_summary, overall_kpis, qa_csat_correlation
)
from scripts.alert_system import QA_THRESHOLD, CSAT_THRESHOLD, identify_low_performers

# ── page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="QA Monitoring System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

PALETTE  = "#2563EB"
ACCENT   = "#DC2626"
BG_WHITE = "#F8FAFC"

sns.set_theme(style="whitegrid", palette="deep", font_scale=1.0)


# ── data loading ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)   # re-load every 5 minutes so cron updates appear
def get_data() -> pd.DataFrame:
    data_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "qa_data.csv",
    )
    if not os.path.exists(data_path):
        st.error(
            "⚠️  Dataset not found. "
            "Please run `python run_pipeline.py` first to generate data."
        )
        st.stop()
    return load_data(data_path)


# ── sidebar ───────────────────────────────────────────────────────────────────
def sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.title("🔍  Filters")

    # Date range
    min_date = df["Date"].min().date()
    max_date = df["Date"].max().date()
    date_range = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if len(date_range) == 2:
        start, end = date_range
        df = df[(df["Date"].dt.date >= start) & (df["Date"].dt.date <= end)]

    # Issue type
    all_issues  = sorted(df["Issue Type"].unique())
    sel_issues  = st.sidebar.multiselect(
        "Issue types", all_issues, default=all_issues
    )
    if sel_issues:
        df = df[df["Issue Type"].isin(sel_issues)]

    # Agent
    all_agents  = sorted(df["Agent Name"].unique())
    sel_agents  = st.sidebar.multiselect("Agents", all_agents, default=all_agents)
    if sel_agents:
        df = df[df["Agent Name"].isin(sel_agents)]

    st.sidebar.markdown("---")
    st.sidebar.metric("Filtered tickets", f"{len(df):,}")

    return df


# ── KPI cards ─────────────────────────────────────────────────────────────────
def render_kpis(df: pd.DataFrame) -> None:
    kpis = overall_kpis(df)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📈  Avg QA Score",      f"{kpis['avg_qa_score']:.1f} / 100")
    c2.metric("😊  Avg CSAT",          f"{kpis['avg_csat']:.2f} / 5")
    c3.metric("🚨  Escalation Rate",   f"{kpis['escalation_pct']:.1f}%")
    c4.metric("🔗  QA ↔ CSAT Corr.",  f"{kpis['qa_csat_corr']:.3f}")


# ── charts ────────────────────────────────────────────────────────────────────
def chart_qa_distribution(df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7, 3.5), facecolor=BG_WHITE)
    ax.set_facecolor(BG_WHITE)
    sns.histplot(df["QA Score"], bins=25, color=PALETTE, edgecolor="white",
                 alpha=0.85, kde=True, line_kws={"color": ACCENT, "lw": 2}, ax=ax)
    ax.axvline(QA_THRESHOLD, color=ACCENT, linestyle="--", lw=1.6,
               label=f"Alert threshold ({QA_THRESHOLD})")
    ax.set_title("QA Score Distribution", fontweight="bold")
    ax.set_xlabel("QA Score"); ax.set_ylabel("Tickets")
    ax.legend(frameon=False, fontsize=9)
    plt.tight_layout()
    return fig


def chart_csat_vs_qa(df: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(7, 3.5), facecolor=BG_WHITE)
    ax.set_facecolor(BG_WHITE)
    jqa  = df["QA Score"] + np.random.uniform(-0.4, 0.4, len(df))
    jcat = df["CSAT"]      + np.random.uniform(-0.07, 0.07, len(df))
    ax.scatter(jqa, jcat, alpha=0.12, s=8, color=PALETTE, rasterized=True)
    z  = np.polyfit(df["QA Score"], df["CSAT"], 1)
    xr = np.linspace(df["QA Score"].min(), df["QA Score"].max(), 200)
    ax.plot(xr, np.poly1d(z)(xr), color=ACCENT, lw=2, label="Trend")
    corr = df["QA Score"].corr(df["CSAT"])
    ax.set_title(f"CSAT vs QA Score  (r = {corr:.3f})", fontweight="bold")
    ax.set_xlabel("QA Score"); ax.set_ylabel("CSAT")
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.legend(frameon=False, fontsize=9)
    plt.tight_layout()
    return fig


def chart_escalation_by_issue(df: pd.DataFrame) -> plt.Figure:
    issues = issue_summary(df).sort_values("Escalation_Pct", ascending=True)
    fig, ax = plt.subplots(figsize=(7, 3.5), facecolor=BG_WHITE)
    ax.set_facecolor(BG_WHITE)
    colors = [ACCENT if p > 15 else PALETTE for p in issues["Escalation_Pct"]]
    bars = ax.barh(issues["Issue Type"], issues["Escalation_Pct"],
                   color=colors, edgecolor="white", height=0.5)
    for bar, val in zip(bars, issues["Escalation_Pct"]):
        ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}%", va="center", fontsize=9)
    ax.set_title("Escalation Rate by Issue Type", fontweight="bold")
    ax.set_xlabel("Escalation Rate (%)")
    ax.set_xlim(0, issues["Escalation_Pct"].max() + 7)
    plt.tight_layout()
    return fig


# ── tables ────────────────────────────────────────────────────────────────────
def render_agent_tables(df: pd.DataFrame) -> None:
    agents   = agent_summary(df)
    low_perf = identify_low_performers(agents)

    display_cols = [
        "Agent Name", "Avg_QA_Score", "Avg_CSAT",
        "Avg_Resolution", "Escalation_Pct", "Total_Tickets",
    ]
    col_labels = {
        "Agent Name": "Agent",
        "Avg_QA_Score": "Avg QA",
        "Avg_CSAT": "Avg CSAT",
        "Avg_Resolution": "Avg Res. (min)",
        "Escalation_Pct": "Escalation %",
        "Total_Tickets": "Tickets",
    }

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("🏆  Top Performers (by QA Score)")
        top5 = agents.head(5)[display_cols].rename(columns=col_labels)
        st.dataframe(
            top5.style.applymap(
            lambda v: "background-color:#16a34a"
            if isinstance(v, float) and v >= 85 else "",
            subset=["Avg QA"],
        ),
         use_container_width=True, hide_index=True)

    with col_b:
        st.subheader("⚠️  Low-Performing Agents")
        if low_perf.empty:
            st.success("No low-performing agents detected under current filters.")
        else:
            lp = low_perf[display_cols].rename(columns=col_labels)
            st.dataframe(
                lp.style.applymap(
                    lambda v: "background-color:#7f1d1d" 
                    if isinstance(v, float) and v < QA_THRESHOLD else "",
                    subset=["Avg QA"],
                ),
                use_container_width=True, hide_index=True,
            )


# ── main layout ───────────────────────────────────────────────────────────────
def main():
    st.title("📊  QA Monitoring and Alert System")
    st.caption("Real-time quality analytics for customer support teams")
    st.markdown("---")

    raw_df = get_data()
    df     = sidebar_filters(raw_df)

    # KPIs
    render_kpis(df)
    st.markdown("---")

    # Charts row
    st.subheader("📉  Analytics Charts")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.pyplot(chart_qa_distribution(df), use_container_width=True)
    with c2:
        st.pyplot(chart_csat_vs_qa(df), use_container_width=True)
    with c3:
        st.pyplot(chart_escalation_by_issue(df), use_container_width=True)

    st.markdown("---")

    # Agent tables
    render_agent_tables(df)

    st.markdown("---")
    st.caption(
        "Data refreshes automatically every 5 minutes. "
        "Re-run `python run_pipeline.py` to update the dataset."
    )


if __name__ == "__main__":
    main()
