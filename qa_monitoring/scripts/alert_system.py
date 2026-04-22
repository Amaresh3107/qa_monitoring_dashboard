"""
alert_system.py
---------------
Scans the QA dataset for low-performing agents and writes timestamped
alert entries to output/alerts.log.

Alert thresholds:
  QA Score < 70   →  low quality flag
  CSAT < 3        →  poor customer satisfaction flag

Each alert line includes:
  [TIMESTAMP]  ALERT | Agent: <name> | Metric: <which> | Value: <val> | Tickets: <n>
"""

import os
import sys
from datetime import datetime
from typing import Optional, List

import pandas as pd

# Allow running from repo root or from scripts/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.analyze_data import load_data, agent_summary

# ── thresholds ────────────────────────────────────────────────────────────────
QA_THRESHOLD   = 70.0
CSAT_THRESHOLD = 3.0

OUTPUT_DIR  = "output"
ALERTS_FILE = os.path.join(OUTPUT_DIR, "alerts.log")


def identify_low_performers(agents: pd.DataFrame) -> pd.DataFrame:
    """
    Return agents whose average QA Score OR average CSAT falls below
    the configured thresholds.
    """
    mask = (
        (agents["Avg_QA_Score"] < QA_THRESHOLD) |
        (agents["Avg_CSAT"]     < CSAT_THRESHOLD)
    )
    return agents[mask].copy()


def build_alert_lines(low_performers: pd.DataFrame) -> list[str]:
    """
    Build a list of formatted alert strings for each low-performing agent.
    Multiple alerts can be raised per agent (one per failing metric).
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = []

    for _, row in low_performers.iterrows():
        agent   = row["Agent Name"]
        tickets = int(row["Total_Tickets"])

        if row["Avg_QA_Score"] < QA_THRESHOLD:
            lines.append(
                f"[{timestamp}]  ALERT | Agent: {agent:<20} | "
                f"Metric: Avg QA Score | Value: {row['Avg_QA_Score']:.2f} "
                f"(threshold: {QA_THRESHOLD}) | Tickets: {tickets}"
            )

        if row["Avg_CSAT"] < CSAT_THRESHOLD:
            lines.append(
                f"[{timestamp}]  ALERT | Agent: {agent:<20} | "
                f"Metric: Avg CSAT     | Value: {row['Avg_CSAT']:.2f} "
                f"(threshold: {CSAT_THRESHOLD}) | Tickets: {tickets}"
            )

    return lines


def write_alerts(lines: list[str], path: str = ALERTS_FILE) -> None:
    """Append alert lines to the log file (creates file if absent)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "a", encoding="utf-8") as f:
        separator = "-" * 90
        f.write(f"\n{separator}\n")
        f.write(
            f"  RUN STARTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            f"  |  Alerts generated: {len(lines)}\n"
        )
        f.write(f"{separator}\n")
        for line in lines:
            f.write(line + "\n")

    print(f"✅  {len(lines)} alert(s) written → {path}")


def run_alerts(df: Optional[pd.DataFrame] = None) -> List[str]:
    """
    End-to-end alert pipeline.
    Returns the list of alert strings (useful for dashboard / report).
    """
    if df is None:
        df = load_data()

    agents        = agent_summary(df)
    low_perf      = identify_low_performers(agents)
    alert_lines   = build_alert_lines(low_perf)

    write_alerts(alert_lines)
    return alert_lines


def main():
    print("=" * 60)
    print("QA MONITORING – ALERT SYSTEM")
    print("=" * 60)

    df           = load_data()
    agents       = agent_summary(df)
    low_perf     = identify_low_performers(agents)

    print(f"\n⚠️   Low-performing agents detected: {len(low_perf)}")
    if not low_perf.empty:
        cols = ["Agent Name", "Avg_QA_Score", "Avg_CSAT",
                "Escalation_Pct", "Total_Tickets"]
        print(low_perf[cols].to_string(index=False))

    alert_lines = build_alert_lines(low_perf)
    write_alerts(alert_lines)


if __name__ == "__main__":
    main()
