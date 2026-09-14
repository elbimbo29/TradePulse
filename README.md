# TradePulse 🚀

TradePulse is a multi-agent financial monitoring dashboard built with Python, Streamlit, SQLite, Finnhub, and OpenAI. It orchestrates automated data collection, custom threshold breach detection, AI-powered news sentiment analysis, and real-time database logging into a clean, interactive user interface.

---

## Architecture & Pipeline

TradePulse follows a modular multi-agent pipeline orchestrated via `main.py`:

1. **Collector Agent (`agents/collector.py`):** Fetches real-time stock quotes and recent financial news articles using the Finnhub API.
2. **Anomaly Agent (`agents/anomaly.py`):** Evaluates incoming market data against statistical bounds and variance rules to flag unusual behavior.
3. **Threshold Agent (`agents/threshold.py`):** Enforces strict user-defined price boundaries (minimum and maximum limits set in the sidebar) to trigger alerts.
4. **Sentiment Agent (`agents/sentiment.py`):** Passes collected news headlines through OpenAI to perform market diagnosis and categorize sentiment (Bullish, Bearish, or Neutral).
5. **Dispatcher Agent (`agents/dispatcher.py`):** Manages alert routing and communications across pipeline components based on anomaly and threshold flags.
6. **Database Agent (`database.py`):** Persists metrics, price tracking histories, and sentiment logs locally into SQLite (`tradepulse.db`).
7. **Background Scheduler (`scheduler.py`):** Handles automated, periodic background polling of the pipeline outside of manual UI triggers.
8. **Monitoring Interface (`app.py`):** A Streamlit dashboard featuring manual pipeline triggers, interactive Plotly charts with threshold overlays, live auto-refresh logs, and CSV export tools.

---

## Project Structure

```text
TradePulse/
├── agents/
│   ├── anomaly.py       # Statistical and variance anomaly detection
│   ├── collector.py     # Finnhub API market data & news collector
│   ├── dispatcher.py    # Alert routing and communication dispatcher
│   ├── sentiment.py     # OpenAI news sentiment analysis agent
│   └── threshold.py     # Strict user-defined price limit enforcement
├── .env                 # Environment variables (API keys)
├── .gitignore           # Excluded files (venv, db, caches)
├── app.py               # Streamlit monitoring dashboard UI
├── database.py          # SQLite database setup & logging handlers
├── main.py              # Pipeline orchestrator
├── requirements.txt     # Python project dependencies
└── scheduler.py         # Automated background polling scheduler
```
---
## 🛠️ Tech Stack

* **Core Language:** Python 3.10+
* **Dashboard & UI:** [Streamlit](https://streamlit.io/) (interactive widgets, state management, real-time layout)
* **Data Processing & Manipulation:** [Pandas](https://pandas.pydata.org/) (dataframe formatting, SQLite query mapping, time-series organization)
* **Data Persistence:** SQLite (`sqlite3`) for local, lightweight transactional logging
* **Financial Data Provider:** [Finnhub API](https://finnhub.io/) (live stock quotes and recent financial news feeds)
* **AI & NLP Intelligence:** [OpenAI API](https://openai.com/) (automated news sentiment classification and market diagnosis)
* **Data Visualization:** [Plotly](https://plotly.com/) (interactive time-series charts, dynamic threshold overlays)
* **Version Control & Collaboration:** Git & GitHub
