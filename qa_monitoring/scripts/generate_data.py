"""
generate_data.py
----------------
Generates a realistic 5000-row dataset simulating a customer support
QA monitoring system (Amazon-style). Saves output to data/qa_data.csv.

Realistic patterns embedded:
  - Lower QA scores slightly increase escalation probability
  - Higher resolution times slightly reduce CSAT scores
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# ── reproducibility ──────────────────────────────────────────────────────────
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# ── constants ────────────────────────────────────────────────────────────────
NUM_ROWS   = 5000
START_DATE = datetime(2024, 1, 1)
END_DATE   = datetime(2024, 12, 31)

AGENTS = [
    "Alice Johnson", "Bob Martinez", "Carol White", "David Lee",
    "Emma Davis", "Frank Wilson", "Grace Brown", "Henry Taylor",
    "Isabelle Moore", "James Anderson", "Karen Thomas", "Liam Jackson",
    "Mia Harris", "Noah Clark", "Olivia Lewis", "Paul Walker",
    "Quinn Allen", "Rachel Young", "Samuel King", "Tina Scott",
]

ISSUE_TYPES = ["Delivery", "Refund", "Account", "Payment", "Product", "Technical"]

# Each agent has a hidden "skill level" (0–1) that influences their metrics
AGENT_SKILL = {agent: round(random.uniform(0.3, 1.0), 2) for agent in AGENTS}


def random_date(start: datetime, end: datetime) -> str:
    """Return a random date string between start and end."""
    delta = (end - start).days
    return (start + timedelta(days=random.randint(0, delta))).strftime("%Y-%m-%d")


def generate_qa_score(skill: float) -> int:
    """
    QA Score: 50–100.
    Agents with higher skill tend to score higher, with some noise.
    """
    base  = 50 + skill * 50          # range: 50 – 100
    noise = np.random.normal(0, 5)   # ±5 natural variation
    return int(np.clip(base + noise, 50, 100))


def generate_resolution_time(issue: str, skill: float) -> int:
    """
    Resolution time in minutes (5–240).
    Complex issues (Refund, Technical) take longer on average.
    Higher-skill agents resolve faster.
    """
    base_times = {
        "Delivery": 30, "Refund": 60, "Account": 25,
        "Payment": 50,  "Product": 20, "Technical": 80,
    }
    base  = base_times[issue]
    skill_factor = 1.5 - skill          # skill=1 → ×0.5, skill=0 → ×1.5
    noise = np.random.normal(0, 10)
    return int(np.clip(base * skill_factor + noise, 5, 240))


def generate_csat(resolution_time: int, qa_score: int) -> int:
    """
    CSAT: 1–5.
    Higher resolution time slightly reduces CSAT.
    Higher QA score slightly boosts CSAT.
    """
    # normalise both inputs to 0–1 range
    time_penalty = resolution_time / 240       # 0 (fast) → 1 (slow)
    qa_bonus     = (qa_score - 50) / 50        # 0 (low QA) → 1 (high QA)

    base  = 3.0
    score = base - 1.5 * time_penalty + 1.5 * qa_bonus
    noise = np.random.normal(0, 0.4)
    return int(np.clip(round(score + noise), 1, 5))


def generate_escalation(qa_score: int) -> str:
    """
    Escalation: Yes/No.
    Lower QA score → higher probability of escalation.
    """
    # probability decreases linearly from ~40 % (QA=50) to ~5 % (QA=100)
    prob = 0.40 - (qa_score - 50) * (0.35 / 50)
    return "Yes" if random.random() < prob else "No"


def generate_dataset(n: int = NUM_ROWS) -> pd.DataFrame:
    """Build and return the full dataset as a DataFrame."""
    records = []
    for _ in range(n):
        agent       = random.choice(AGENTS)
        skill       = AGENT_SKILL[agent]
        issue       = random.choice(ISSUE_TYPES)
        qa_score    = generate_qa_score(skill)
        res_time    = generate_resolution_time(issue, skill)
        csat        = generate_csat(res_time, qa_score)
        escalation  = generate_escalation(qa_score)
        date        = random_date(START_DATE, END_DATE)

        records.append({
            "Agent Name":       agent,
            "Issue Type":       issue,
            "QA Score":         qa_score,
            "CSAT":             csat,
            "Resolution Time":  res_time,
            "Escalation":       escalation,
            "Date":             date,
        })

    return pd.DataFrame(records)


def main():
    # Ensure the data folder exists
    os.makedirs("data", exist_ok=True)

    print("Generating dataset …")
    df = generate_dataset()

    output_path = os.path.join("data", "qa_data.csv")
    df.to_csv(output_path, index=False)

    print(f"✅  Dataset saved → {output_path}")
    print(f"   Rows: {len(df):,}  |  Columns: {list(df.columns)}")
    print(df.head(5).to_string(index=False))


if __name__ == "__main__":
    main()
