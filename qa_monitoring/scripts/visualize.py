"""
visualize.py
------------
Generates three analysis charts and saves them to output/:

  1. qa_score_distribution.png  – histogram of QA scores across all tickets
  2. csat_vs_qa_score.png       – scatter plot with trend line
  3. escalation_by_issue.png    – horizontal bar chart of escalation rate per issue type

Uses seaborn + matplotlib for polished, readable charts.
"""

import os
import sys

import matplotlib
matplotlib.use("Agg")          # non-interactive backend – safe for servers / cron
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.analyze_data import load_data, issue_summary

OUTPUT_DIR = "output"

# ── global style ──────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="deep", font_scale=1.1)
PALETTE   = "#2563EB"          # primary blue
ACCENT    = "#DC2626"          # alert red
BG_COLOR  = "#F8FAFC"
FIG_DPI   = 150


def save_fig(fig: plt.Figure, filename: str) -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(path, dpi=FIG_DPI, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close(fig)
    print(f"  ✅  Saved → {path}")


# ── Chart 1: QA Score Distribution ───────────────────────────────────────────

def plot_qa_distribution(df: pd.DataFrame) -> None:
    """Histogram of QA score with a density curve overlay."""
    fig, ax = plt.subplots(figsize=(9, 5), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    sns.histplot(
        df["QA Score"], bins=25, color=PALETTE,
        edgecolor="white", alpha=0.85, kde=True,
        line_kws={"color": ACCENT, "lw": 2},
        ax=ax,
    )

    # Threshold line at 70
    ax.axvline(70, color=ACCENT, linestyle="--", lw=1.8, label="Alert threshold (70)")

    ax.set_title("QA Score Distribution", fontsize=15, fontweight="bold", pad=14)
    ax.set_xlabel("QA Score")
    ax.set_ylabel("Number of Tickets")
    ax.legend(frameon=False)

    # Summary stats annotation
    mean_qa = df["QA Score"].mean()
    ax.annotate(
        f"Mean: {mean_qa:.1f}",
        xy=(mean_qa, ax.get_ylim()[1] * 0.85),
        xytext=(mean_qa + 3, ax.get_ylim()[1] * 0.85),
        fontsize=10, color=PALETTE,
        arrowprops=dict(arrowstyle="->", color=PALETTE, lw=1.2),
    )

    save_fig(fig, "qa_score_distribution.png")


# ── Chart 2: CSAT vs QA Score ─────────────────────────────────────────────────

def plot_csat_vs_qa(df: pd.DataFrame) -> None:
    """
    Scatter plot of CSAT vs QA Score with a linear regression trend line.
    Points are jittered because both variables have limited discrete values.
    """
    fig, ax = plt.subplots(figsize=(9, 5), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    # Jitter for visual clarity
    jittered_qa   = df["QA Score"]   + np.random.uniform(-0.5, 0.5, len(df))
    jittered_csat = df["CSAT"]        + np.random.uniform(-0.08, 0.08, len(df))

    ax.scatter(
        jittered_qa, jittered_csat,
        alpha=0.15, s=10, color=PALETTE, rasterized=True,
    )

    # Trend line via numpy polyfit
    z    = np.polyfit(df["QA Score"], df["CSAT"], 1)
    p    = np.poly1d(z)
    x_ln = np.linspace(df["QA Score"].min(), df["QA Score"].max(), 200)
    ax.plot(x_ln, p(x_ln), color=ACCENT, lw=2.2, label="Trend line")

    corr = df["QA Score"].corr(df["CSAT"])
    ax.set_title(
        f"CSAT vs QA Score  (r = {corr:.3f})",
        fontsize=15, fontweight="bold", pad=14,
    )
    ax.set_xlabel("QA Score")
    ax.set_ylabel("CSAT (1–5)")
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.legend(frameon=False)

    save_fig(fig, "csat_vs_qa_score.png")


# ── Chart 3: Escalation Rate by Issue Type ────────────────────────────────────

def plot_escalation_by_issue(df: pd.DataFrame) -> None:
    """Horizontal bar chart showing escalation % per issue type."""
    issues = issue_summary(df).sort_values("Escalation_Pct", ascending=True)

    fig, ax = plt.subplots(figsize=(9, 5), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    colors = [ACCENT if p > 15 else PALETTE for p in issues["Escalation_Pct"]]
    bars = ax.barh(
        issues["Issue Type"], issues["Escalation_Pct"],
        color=colors, edgecolor="white", height=0.55,
    )

    # Data labels
    for bar, val in zip(bars, issues["Escalation_Pct"]):
        ax.text(
            bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
            f"{val:.1f}%", va="center", fontsize=10,
        )

    ax.xaxis.set_major_formatter(mtick.PercentFormatter())
    ax.set_title(
        "Escalation Rate by Issue Type",
        fontsize=15, fontweight="bold", pad=14,
    )
    ax.set_xlabel("Escalation Rate (%)")
    ax.set_xlim(0, issues["Escalation_Pct"].max() + 6)

    # Legend
    from matplotlib.patches import Patch
    legend_els = [
        Patch(color=ACCENT, label="High escalation (>15 %)"),
        Patch(color=PALETTE, label="Normal"),
    ]
    ax.legend(handles=legend_els, frameon=False, loc="lower right")

    save_fig(fig, "escalation_by_issue.png")


# ── main ──────────────────────────────────────────────────────────────────────

def run_visualizations(df: Optional[pd.DataFrame] = None) -> None:
    if df is None:
        df = load_data()

    print("Generating charts …")
    plot_qa_distribution(df)
    plot_csat_vs_qa(df)
    plot_escalation_by_issue(df)
    print("All charts saved.")


def main():
    print("=" * 60)
    print("QA MONITORING – VISUALIZATIONS")
    print("=" * 60)
    run_visualizations()


if __name__ == "__main__":
    main()
