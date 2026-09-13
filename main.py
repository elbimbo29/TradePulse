"""Main orchestration script for the TradePulse monitoring pipeline."""

from agents.collector import fetch_stock_data
from agents.threshold import evaluate_thresholds
from agents.anomaly import detect_anomaly
from agents.dispatcher import dispatch_alert


def run_pipeline(symbol: str, rules: dict, price_history: list, api_key: str) -> dict:
	"""Fetch data, evaluate rules, detect anomalies, and dispatch alerts."""
	stock_data = fetch_stock_data(symbol, api_key)
	threshold_result = evaluate_thresholds(stock_data, rules)
	anomaly_result = detect_anomaly(price_history)

	threshold_triggered = bool(threshold_result)
	anomaly_triggered = bool(anomaly_result)
	dispatched_alerts = []

	if threshold_triggered:
		dispatched_alerts.append(
			dispatch_alert(symbol, "threshold", threshold_result)
		)
	if anomaly_triggered:
		dispatched_alerts.append(
			dispatch_alert(symbol, "anomaly", anomaly_result)
		)

	return {
		"symbol": symbol,
		"stock_data": stock_data,
		"threshold_result": threshold_result,
		"anomaly_result": anomaly_result,
		"threshold_triggered": threshold_triggered,
		"anomaly_triggered": anomaly_triggered,
		"dispatched_alerts": dispatched_alerts,
	}


if __name__ == "__main__":
	print(
		run_pipeline(
			symbol="AAPL",
			rules={"min_price": 150.0, "max_price": 250.0},
			price_history=[190.0, 191.2, 190.8, 192.1, 191.7],
			api_key="mock-api-key",
		)
	)
