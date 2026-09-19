import csv

data = [
    ["Test Module", "What We Are Testing", "Prerequisites", "Command / Execution", "Expected Result / Outcome"],
    ["1. Guardrail Validation", "Interception of prompt injections and SQL payloads.", "Docker stack running (docker compose up -d)", "python -c \"from main import run_pipeline; run_pipeline(\x27IBM; DROP TABLE users;\x27)\"", "Console outputs [GUARDRAIL BLOCKED]. Execution halts safely."],
    ["2. OTel / Prometheus Telemetry", "Emission of metrics/spans via OTLP gRPC to Prometheus.", "Docker stack active; main.py executed.", "Check http://localhost:9090 or collector logs.", "Metrics like guardrail_blocks_total increment cleanly with no gRPC errors."],
    ["3. Grafana Provisioning", "Automatic provisioning of Prometheus datasource & dashboard JSON.", "Mounted grafana-provisioning/ directory.", "Access http://localhost:3001", "Prometheus data source active; TradePulse dashboard panels auto-populated."],
    ["4. DeepEval Quality Testing", "LLM output quality, hallucination score, and disclaimer compliance.", "API keys configured in .env; deepeval installed.", "deepeval test run tests/test_sentiment_eval.py", "All test assertions PASS. Sentiment analysis includes mandatory disclaimer."],
    ["5. SQLite Data Persistence", "Verification of stored market data, news metadata, and audit logs.", "main.py executed successfully.", "Inspect SQLite DB via python or sqlite3 CLI.", "Table contains valid stock symbol, fetched price, and timestamp entries."]
]

with open("tradepulse_test_plan.csv", mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(data)

print("File created successfully: tradepulse_test_plan.csv")

