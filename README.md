# ⚡ TradePulse - LLM Test Pipeline Observability

A full-stack observability and evaluation pipeline for Large Language Model (LLM) testing suites. This project integrates Python-based LLM testing and validation frameworks with an OpenTelemetry-driven telemetry stack, fully dockerized with **Tempo**, **Loki**, **Prometheus**, and **Grafana**.

---

## 🏗️ Architecture Overview

               ┌──────────────────────────────────────────┐
               │        Python Test Pipeline              │
               │ (pytest, DeepEval, Guardrails, Tenacity) │
               └────────────────────┬─────────────────────┘
                                    │ OTLP (gRPC / 4317)
                                    ▼
               ┌──────────────────────────────────────────┐
               │    OpenTelemetry Collector (Contrib)     │
               └──────┬─────────────┬──────────────┬──────┘
                      │             │              │
         Traces (OTLP)│  Logs (OTLP)│  Metrics     │
                      ▼             ▼              ▼
                 ┌─────────┐   ┌─────────┐   ┌────────────┐
                 │  Tempo  │   │  Loki   │   │ Prometheus │
                 └────┬────┘   └────┬────┘   └─────┬──────┘
                      │             │              │
                      └─────────────┼──────────────┘
                                    ▼
                             ┌────────────┐
                             │  Grafana   │
                             └────────────┘

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
├── docker-compose.yml          # Observability infrastructure services
├── otel-collector-config.yaml  # OTel pipeline routing rules (Traces, Metrics, Logs)
├── telemetry_config.py         # OTel Python SDK initialization helper
├── run_telemetry_tests.py      # Telemetry pipeline verification script
├── test_stack_components.py    # Full integration test suite
└── README.md                   # Project documentation
```
---
## 🛠️ Tech Stack

### **Python Test Suite & Utilities**
* **`pytest`**: Test runner and execution orchestration.
* **`DeepEval`**: LLM evaluation framework measuring model metrics (faithfulness, confidence scores, answer relevancy).
* **`Guardrails`**: Input/output validation and schema enforcement.
* **`Tenacity`**: Retry resilience and backoff handling for API calls.
* **`structlog`**: Structured JSON logging correlated with OpenTelemetry trace context.
* **`python-dotenv`**: Environment variable management.

### **Observability Stack (Dockerized)**
* **OpenTelemetry Collector**: Unified telemetry ingest pipeline routing signals via OTLP.
* **Grafana Tempo**: Distributed tracing for multi-attempt LLM executions and span timing.
* **Grafana Loki**: Centralized log aggregation with trace-id injection.
* **Prometheus**: Time-series database storing test pass/fail rates and evaluation score distributions.
* **Grafana**: Single pane of glass for unified dashboards and cross-signal correlation.
---

## ⚙️ Installation & Setup

1. **Clone the Repository:**

```bash
git clone [https://github.com/elbimbo29/TradePulse.git](https://github.com/elbimbo29/TradePulse.git)
cd TradePulse
```

2. **Create and Activate a Virtual Environment:**

```powershell
python -m venv venv

# On Windows:
.\venv\Scripts\Activate.ps1

# On macOS/Linux:
source venv/bin/activate
```

3. **Install Dependencies:**

```bash
pip install -r requirements.txt
```

4. **Configure Environment Variables:**

Create a `.env` file in the root directory:

```env
FINNHUB_API_KEY=your_finnhub_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```
---

## 🚀 Running the Stack & Tests

### **2. Running Telemetry Tests**
```text
Execute your telemetry initialization test script or run the integration suite via `pytest`:

```powershell
# Run telemetry test script
python run_telemetry_tests.py

# Or run via pytest
pytest -v test_stack_components.py
**
```
---