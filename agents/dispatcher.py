"""Alert Dispatcher Agent utilities."""

import os

import requests


def dispatch_alert(alert_type: str, details: dict) -> bool:
	"""Dispatch an alert to stdout and optionally to Slack.

	Args:
		alert_type: Alert type, either ``"THRESHOLD"`` or ``"ANOMALY"``.
		details: Details describing the alert.

	Returns:
		True if the alert was dispatched successfully, otherwise False.
	"""
	if alert_type not in {"THRESHOLD", "ANOMALY"}:
		raise ValueError("alert_type must be 'THRESHOLD' or 'ANOMALY'")

	details_text = ", ".join(f"{key}={value}" for key, value in details.items())
	message = f"[TradePulse Alert] {alert_type}: {details_text}"
	print(message)

	webhook_url = os.getenv("SLACK_WEBHOOK_URL")
	if not webhook_url:
		return True

	try:
		response = requests.post(
			webhook_url,
			json={"text": message},
			timeout=10,
		)
		response.raise_for_status()
	except requests.RequestException:
		return False

	return True
