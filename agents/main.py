"""Orchestrate stock collection, signal evaluation, and alert dispatch."""

from agents.collector import fetch_stock_data
from agents.threshold import evaluate_thresholds
from agents.anomaly import detect_anomaly
from agents.dispatcher import dispatch_alert


def run_pipeline(symbol: str, rules: dict, price_history: list, api_key: str) -> dict:
	"""Run all monitoring steps and return their execution summary."""
	stock_data = fetch_stock_data(symbol, api_key)
	threshold_result = evaluate_thresholds(stock_data, rules)
	anomaly_result = detect_anomaly(price_history)

	threshold_triggered = bool(threshold_result)
	anomaly_triggered = bool(anomaly_result)
	alert_dispatched = False

	if threshold_triggered or anomaly_triggered:
		dispatch_alert(
			{
				"symbol": symbol,
				"threshold": threshold_result,
				"anomaly": anomaly_result,
			}
		)
		alert_dispatched = True

	return {
		"symbol": symbol,
		"stock_data": stock_data,
		"threshold_result": threshold_result,
		"anomaly_result": anomaly_result,
		"threshold_triggered": threshold_triggered,
		"anomaly_triggered": anomaly_triggered,
		"alert_dispatched": alert_dispatched,
	}


if __name__ == "__main__":
	print(
		run_pipeline(
			symbol="AAPL",
			rules={"min_price": 150.0, "max_price": 250.0},
			price_history=[178.2, 179.1, 178.7, 180.0, 181.4],
			api_key="demo-api-key",
		)
	)
