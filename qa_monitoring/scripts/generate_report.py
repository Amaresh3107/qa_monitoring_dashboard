"""
generate_report.py
------------------
Produces a structured summary report CSV at output/report.csv.

Sections written (each clearly labelled):
  1. Overall KPIs
  2. Top-performing agents  (top 5 by Avg QA Score)
  3. Low-performing agents  (QA < 70 OR CSAT < 3)
  4. Issue type breakdown
"""

import os
import sys
from datetime import datetime
import pandas as pd
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.analyze_data import (
    load_data, agent_summary, issue_summary, overall_kpis
)
from scripts.alert_system import (
    QA_THRESHOLD, CSAT_THRESHOLD, identify_low_performers
)

OUTPUT_DIR   = "output"
REPORT_FILE  = os.path.join(OUTPUT_DIR, "report.csv")

TOP_N_AGENTS = 5   # number of top performers to highlight


def build_section_header(title: str) -> pd.DataFrame:
    """Return a single-row DataFrame used as a visual section divider."""
    return pd.DataFrame([{"Section": f"── {title} ──"}])


def kpis_to_df(kpis: dict) -> pd.DataFrame:
    """Convert the KPI dict to a two-column DataFrame."""
    rows = [{"Metric": k.replace("_", " ").title(), "Value": v}
            for k, v in kpis.items()]
    return pd.DataFrame(rows)


def write_report(
    kpis:      dict,
    agents:    pd.DataFrame,
    low_perf:  pd.DataFrame,
    issues:    pd.DataFrame,
    path:      str = REPORT_FILE,
) -> None:
    """
    Write all report sections into a single CSV separated by blank rows
    and header labels.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)

    top_agents = agents.head(TOP_N_AGENTS)

    agent_cols = [
        "Agent Name", "Avg_QA_Score", "Avg_CSAT",
        "Avg_Resolution", "Escalation_Pct", "Total_Tickets",
    ]

    issue_cols = [
        "Issue Type", "Volume", "Avg_QA_Score",
        "Avg_CSAT", "Avg_Resolution", "Escalation_Pct",
    ]

    run_meta = pd.DataFrame([{
        "Report Generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "QA Threshold":     QA_THRESHOLD,
        "CSAT Threshold":   CSAT_THRESHOLD,
    }])

    sections = [
        ("Report Metadata",         run_meta),
        ("Overall KPIs",            kpis_to_df(kpis)),
        (f"Top {TOP_N_AGENTS} Performing Agents",
                                    top_agents[agent_cols]),
        ("Low-Performing Agents",   low_perf[agent_cols] if not low_perf.empty
                                    else pd.DataFrame([{"Note": "No low-performing agents detected"}])),
        ("Issue Type Breakdown",    issues[issue_cols]),
    ]

    with open(path, "w", encoding="utf-8", newline="") as f:
        first = True
        for title, df_section in sections:
            if not first:
                f.write("\n")               # blank separator row
            # Write section header row
            f.write(f"=== {title} ===\n")
            df_section.to_csv(f, index=False)
            first = False

    print(f"✅  Report saved → {path}")


def run_report(df: Optional[pd.DataFrame] = None) -> None:
    """End-to-end report pipeline."""
    if df is None:
        df = load_data()

    agents   = agent_summary(df)
    issues   = issue_summary(df)
    kpis     = overall_kpis(df)
    low_perf = identify_low_performers(agents)

    write_report(kpis, agents, low_perf, issues)


def main():
    print("=" * 60)
    print("QA MONITORING – REPORT GENERATOR")
    print("=" * 60)
    run_report()


if __name__ == "__main__":
    main()
