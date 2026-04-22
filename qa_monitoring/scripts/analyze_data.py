"""
analyze_data.py
---------------
Loads qa_data.csv and computes key QA metrics using Pandas:

  • Average QA score per agent
  • Average resolution time per agent
  • Escalation percentage per agent
  • Overall correlation between QA Score and CSAT
  • Top issue categories by volume and avg QA score

All summary tables are printed to console and returned as DataFrames
for use by other scripts (report generation, alerting, etc.).
"""

import os
import pandas as pd
from typing import Optional


# ── helpers ───────────────────────────────────────────────────────────────────

def load_data(path: str = os.path.join("data", "qa_data.csv")) -> pd.DataFrame:
    """Load the dataset from CSV and do basic type casting."""
    df = pd.read_csv(path, parse_dates=["Date"])
    return df


def agent_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Group by agent and compute:
      - Avg QA Score
      - Avg CSAT
      - Avg Resolution Time (mins)
      - Escalation %
      - Total tickets handled
    """
    summary = (
        df.groupby("Agent Name")
        .agg(
            Avg_QA_Score      = ("QA Score",        "mean"),
            Avg_CSAT          = ("CSAT",             "mean"),
            Avg_Resolution    = ("Resolution Time",  "mean"),
            Total_Tickets     = ("Agent Name",       "count"),
            Escalations       = ("Escalation",       lambda x: (x == "Yes").sum()),
        )
        .reset_index()
    )
    summary["Escalation_Pct"] = (
        summary["Escalations"] / summary["Total_Tickets"] * 100
    ).round(2)

    # Round float columns for readability
    for col in ["Avg_QA_Score", "Avg_CSAT", "Avg_Resolution"]:
        summary[col] = summary[col].round(2)

    return summary.sort_values("Avg_QA_Score", ascending=False)


def issue_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Group by issue type and compute:
      - Volume (ticket count)
      - Avg QA Score
      - Avg CSAT
      - Avg Resolution Time
      - Escalation %
    """
    summary = (
        df.groupby("Issue Type")
        .agg(
            Volume            = ("Issue Type",       "count"),
            Avg_QA_Score      = ("QA Score",         "mean"),
            Avg_CSAT          = ("CSAT",              "mean"),
            Avg_Resolution    = ("Resolution Time",   "mean"),
            Escalations       = ("Escalation",        lambda x: (x == "Yes").sum()),
        )
        .reset_index()
    )
    summary["Escalation_Pct"] = (
        summary["Escalations"] / summary["Volume"] * 100
    ).round(2)

    for col in ["Avg_QA_Score", "Avg_CSAT", "Avg_Resolution"]:
        summary[col] = summary[col].round(2)

    return summary.sort_values("Volume", ascending=False)


def qa_csat_correlation(df: pd.DataFrame) -> float:
    """Return Pearson correlation coefficient between QA Score and CSAT."""
    return round(df["QA Score"].corr(df["CSAT"]), 4)


def overall_kpis(df: pd.DataFrame) -> dict:
    """Return a flat dict of headline KPIs for dashboards / reports."""
    return {
        "total_tickets":      len(df),
        "avg_qa_score":       round(df["QA Score"].mean(), 2),
        "avg_csat":           round(df["CSAT"].mean(), 2),
        "avg_resolution_min": round(df["Resolution Time"].mean(), 2),
        "escalation_pct":     round((df["Escalation"] == "Yes").mean() * 100, 2),
        "qa_csat_corr":       qa_csat_correlation(df),
    }


# ── main ──────────────────────────────────────────────────────────────────────

def run_analysis(df: Optional[pd.DataFrame] = None) -> dict:
    """
    Execute full analysis. If no DataFrame is passed, loads from CSV.
    Returns a dict with all analysis artefacts.
    """
    if df is None:
        df = load_data()

    agents  = agent_summary(df)
    issues  = issue_summary(df)
    kpis    = overall_kpis(df)
    corr    = qa_csat_correlation(df)

    return {
        "df":      df,
        "agents":  agents,
        "issues":  issues,
        "kpis":    kpis,
        "corr":    corr,
    }


def main():
    print("=" * 60)
    print("QA MONITORING – DATA ANALYSIS")
    print("=" * 60)

    results = run_analysis()

    # ── Overall KPIs ──────────────────────────────────────────────
    print("\n📊  Overall KPIs")
    print("-" * 40)
    for k, v in results["kpis"].items():
        print(f"  {k:<25} {v}")

    # ── Agent Summary ─────────────────────────────────────────────
    print("\n👤  Agent Performance Summary (top 10)")
    print("-" * 80)
    print(results["agents"].head(10).to_string(index=False))

    # ── Issue Summary ─────────────────────────────────────────────
    print("\n📦  Issue Type Summary")
    print("-" * 80)
    print(results["issues"].to_string(index=False))

    # ── Correlation ───────────────────────────────────────────────
    print(f"\n🔗  QA Score ↔ CSAT Correlation: {results['corr']}")
    print("    (values close to +1 indicate strong positive relationship)\n")


if __name__ == "__main__":
    main()
