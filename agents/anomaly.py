import numpy as np


def detect_anomaly(
	price_history: list, current_price: float, threshold: float = 2.0
) -> dict:
	"""Detect whether the current price is anomalous relative to its history.

	Args:
		price_history: Historical prices used to calculate the mean and standard
			deviation.
		current_price: Price to evaluate.
		threshold: Absolute z-score threshold for flagging an anomaly.

	Returns:
		A dictionary with ``is_anomaly``, ``z_score``, and ``message`` keys.
	"""
	if len(price_history) < 3:
		return {
			"is_anomaly": False,
			"z_score": 0.0,
			"message": "Insufficient price history to detect an anomaly.",
		}

	prices = np.asarray(price_history, dtype=float)
	mean = np.mean(prices)
	standard_deviation = np.std(prices)

	if standard_deviation == 0:
		return {
			"is_anomaly": False,
			"z_score": 0.0,
			"message": "Cannot calculate a z-score because standard deviation is zero.",
		}

	z_score = float((current_price - mean) / standard_deviation)
	is_anomaly = bool(abs(z_score) > threshold)

	return {
		"is_anomaly": is_anomaly,
		"z_score": z_score,
		"message": "Anomaly detected." if is_anomaly else "No anomaly detected.",
	}
