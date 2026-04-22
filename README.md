# 📊 QA Monitoring and Alert System

A production-style Python project that simulates a **Quality Analyst (QA) Monitoring Workflow** for customer support teams (Amazon-style). It generates realistic data, runs analysis, fires alerts, produces reports, creates charts, and serves an interactive Streamlit dashboard — all automated via cron.

---

## 🗂️ Project Structure

```
qa_monitoring/
├── data/
│   └── qa_data.csv              ← Generated dataset (5 000 rows)
├── scripts/
│   ├── generate_data.py         ← Creates synthetic QA dataset
│   ├── analyze_data.py          ← Pandas-based analysis & KPIs
│   ├── alert_system.py          ← Detects low-performing agents
│   ├── generate_report.py       ← Writes structured CSV report
│   └── visualize.py             ← Saves 3 matplotlib/seaborn charts
├── output/
│   ├── alerts.log               ← Timestamped alert log
│   ├── report.csv               ← Summary report
│   ├── qa_score_distribution.png
│   ├── csat_vs_qa_score.png
│   └── escalation_by_issue.png
├── dashboard/
│   └── app.py                   ← Streamlit dashboard
├── run_pipeline.py              ← Master runner (all steps in sequence)
├── requirements.txt
└── README.md
```

---

## 🛠️ Tools Used

| Tool | Purpose |
|------|---------|
| Python 3.10+ | Core language |
| Pandas | Data manipulation & analysis |
| NumPy | Numerical computations |
| Matplotlib | Chart generation |
| Seaborn | Statistical visualisations |
| Streamlit | Interactive web dashboard |

---

## ⚙️ Setup Instructions

### 1. Clone or download the project

```bash
git clone https://github.com/yourname/qa_monitoring.git
cd qa_monitoring
```

### 2. Create and activate a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Pipeline

Run everything in one command from the project root:

```bash
python run_pipeline.py
```

This executes the 5-step pipeline:

| Step | Script | Output |
|------|--------|--------|
| 1 | `generate_data.py` | `data/qa_data.csv` |
| 2 | `analyze_data.py` | Console summary |
| 3 | `alert_system.py` | `output/alerts.log` |
| 4 | `generate_report.py` | `output/report.csv` |
| 5 | `visualize.py` | 3 × PNG charts |

You can also run each script individually:

```bash
python scripts/generate_data.py
python scripts/analyze_data.py
python scripts/alert_system.py
python scripts/generate_report.py
python scripts/visualize.py
```

---

## 📊 Running the Streamlit Dashboard

```bash
streamlit run dashboard/app.py
```

Open your browser at **http://localhost:8501**.

The dashboard shows:
- 📈 KPI cards: Avg QA, Avg CSAT, Escalation %, Correlation
- Interactive filters (date range, issue type, agent)
- All three charts inline
- Top-performers table and low-performers table (highlighted in red)

---

## ⏰ Automating with Cron (Linux)

Run the pipeline daily at 6:00 AM automatically.

### Step 1 – Get the full path to your Python executable

```bash
which python3
# Example output: /home/youruser/qa_monitoring/venv/bin/python3
```

### Step 2 – Open the crontab editor

```bash
crontab -e
```

### Step 3 – Add the cron job

```cron
# Run QA pipeline every day at 06:00 AM
0 6 * * * /home/youruser/qa_monitoring/venv/bin/python3 \
    /home/youruser/qa_monitoring/run_pipeline.py \
    >> /home/youruser/qa_monitoring/output/cron.log 2>&1
```

### Step 4 – Run every hour (alternative)

```cron
# Run every hour at :00
0 * * * * /home/youruser/qa_monitoring/venv/bin/python3 \
    /home/youruser/qa_monitoring/run_pipeline.py \
    >> /home/youruser/qa_monitoring/output/cron.log 2>&1
```

### Step 5 – Verify the cron job is registered

```bash
crontab -l
```

The pipeline logs will appear in `output/cron.log`.

---

## 💡 Business Insights Explained

### Why QA Score matters
QA scores reflect how well an agent follows company processes — correct greetings, empathy, proper resolution steps, compliance. Low QA scores are early warning signs of customer dissatisfaction.

### Why CSAT matters
Customer Satisfaction (1–5) directly measures customer happiness. CSAT < 3 is a red flag that the customer experience needs immediate intervention.

### Correlation between QA and CSAT
The positive Pearson correlation (r ≈ 0.4–0.6) confirms that **better process adherence leads to happier customers**. This validates investing in coaching low-QA agents.

### Escalation Rate by Issue
Issues like **Refund** and **Technical** tend to have higher escalation rates because they are inherently more complex and emotionally charged. Teams should allocate senior agents to these queues.

### Alert thresholds
| Metric | Alert Threshold | Why |
|--------|---------------|-----|
| Avg QA Score | < 70 | Below 70 indicates consistent process failures |
| Avg CSAT | < 3 | Below neutral; customers are likely dissatisfied |

### Resolution Time
Longer resolution times (> 60 min) are correlated with lower CSAT — customers dislike waiting. Identify agents with high resolution times for workflow training.

---

## 🔄 Extending the Project

- **Email alerts** – pipe `output/alerts.log` into `smtplib` to send daily digest emails
- **Real data** – replace `generate_data.py` with a connector to your CRM / ticketing system
- **Database** – swap CSV for SQLite or PostgreSQL for historical trend analysis
- **Slack notifications** – use the Slack API to push alerts to a `#qa-alerts` channel

---

## 📄 License

MIT License – free to use and adapt.
