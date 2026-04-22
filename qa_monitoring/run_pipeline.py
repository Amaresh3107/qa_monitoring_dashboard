"""
run_pipeline.py
---------------
Master script – runs the full QA Monitoring pipeline in sequence:

  Step 1: Generate dataset         (scripts/generate_data.py)
  Step 2: Analyse data             (scripts/analyze_data.py)
  Step 3: Raise alerts             (scripts/alert_system.py)
  Step 4: Generate report CSV      (scripts/generate_report.py)
  Step 5: Generate visualisations  (scripts/visualize.py)

Usage:
  python run_pipeline.py

Intended to be run via cron for automated monitoring.
"""

import sys
import time
from datetime import datetime

# ── helpers ───────────────────────────────────────────────────────────────────

def section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def elapsed(start: float) -> str:
    secs = time.time() - start
    return f"{secs:.1f}s"


# ── pipeline ──────────────────────────────────────────────────────────────────

def main():
    pipeline_start = time.time()
    print(f"\n🚀  QA Monitoring Pipeline started at "
          f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # ── Step 1: Generate data ────────────────────────────────────────────────
    section("Step 1 / 5 – Generating Dataset")
    t = time.time()
    from scripts.generate_data import main as gen_main
    gen_main()
    print(f"  ⏱  Done in {elapsed(t)}")

    # ── Step 2: Analyse ───────────────────────────────────────────────────────
    section("Step 2 / 5 – Running Analysis")
    t = time.time()
    from scripts.analyze_data import main as ana_main
    ana_main()
    print(f"  ⏱  Done in {elapsed(t)}")

    # ── Step 3: Alerts ────────────────────────────────────────────────────────
    section("Step 3 / 5 – Generating Alerts")
    t = time.time()
    from scripts.alert_system import main as alert_main
    alert_main()
    print(f"  ⏱  Done in {elapsed(t)}")

    # ── Step 4: Report ────────────────────────────────────────────────────────
    section("Step 4 / 5 – Generating Report")
    t = time.time()
    from scripts.generate_report import main as report_main
    report_main()
    print(f"  ⏱  Done in {elapsed(t)}")

    # ── Step 5: Visualisations ───────────────────────────────────────────────
    section("Step 5 / 5 – Creating Visualisations")
    t = time.time()
    from scripts.visualize import main as viz_main
    viz_main()
    print(f"  ⏱  Done in {elapsed(t)}")

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print(f"  ✅  Pipeline complete in {elapsed(pipeline_start)}")
    print(f"  📁  Output files:")
    print(f"       data/qa_data.csv")
    print(f"       output/alerts.log")
    print(f"       output/report.csv")
    print(f"       output/qa_score_distribution.png")
    print(f"       output/csat_vs_qa_score.png")
    print(f"       output/escalation_by_issue.png")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
