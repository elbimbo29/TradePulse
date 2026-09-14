"""SQLite persistence helpers for TradePulse monitoring data."""

import sqlite3
import json
import ast
from datetime import datetime
from pathlib import Path

import pandas as pd


DB_NAME = "tradepulse.db"
DATABASE_PATH = Path(__file__).with_name(DB_NAME)


def init_db() -> None:
	"""Create the monitoring log table if it does not already exist."""
	with sqlite3.connect(DATABASE_PATH) as connection:
		connection.execute(
			"""
			CREATE TABLE IF NOT EXISTS price_logs (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
				symbol TEXT,
				price REAL,
				is_anomaly INTEGER,
				z_score REAL,
				anomaly_metrics TEXT,
				alert_triggered INTEGER,
				reason TEXT,
				sentiment TEXT,
				summary TEXT
			)
			"""
		)


		columns = {
			row[1] for row in connection.execute("PRAGMA table_info(price_logs)")
		}
		if "anomaly_metrics" not in columns:
			connection.execute("ALTER TABLE price_logs ADD COLUMN anomaly_metrics TEXT")
def log_price(
	symbol: str,
	price: float,
	anomaly_metrics: dict,
	alert_triggered: bool,
	reason: str,
	sentiment: str = "N/A",
	summary: str = "",
) -> None:
	"""Save one price monitoring event to the database."""
	init_db()
	if isinstance(anomaly_metrics, str):
		try:
			metrics = json.loads(anomaly_metrics)
			extra = False
		except (json.JSONDecodeError, TypeError, ValueError):
			try:
				metrics = ast.literal_eval(anomaly_metrics)
			except (ValueError, SyntaxError, TypeError, MemoryError):
				metrics = {}
	else:
		metrics = anomaly_metrics
	if not isinstance(metrics, dict):
		metrics = {}
	is_anomaly = bool(metrics.get("is_anomaly", metrics.get("anomaly", False)))
	z_score = metrics.get("z_score")
	with sqlite3.connect(DATABASE_PATH) as connection:
		connection.execute(
			"""
			INSERT INTO price_logs (
				symbol, price, is_anomaly, z_score, anomaly_metrics,
				alert_triggered, reason, sentiment, summary
			) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
			""",
			(
				symbol,
				price,
				int(is_anomaly),
				z_score,
				json.dumps(metrics),
				int(alert_triggered),
				reason,
				sentiment,
				summary,
			),
		)


def log_sentiment_event(
	symbol: str,
	price: float,
	alert_triggered: bool,
	sentiment_data: dict,
) -> None:
	"""Save one sentiment monitoring event to the database."""
	init_db()
	with sqlite3.connect(DATABASE_PATH) as connection:
		connection.execute(
			"""
			INSERT INTO sentiment_logs (
				symbol, price, alert_triggered, sentiment, summary
			) VALUES (?, ?, ?, ?, ?)
			""",
			(
				symbol,
				price,
				int(alert_triggered),
				sentiment_data.get("sentiment"),
				sentiment_data.get("summary"),
			),
		)


def save_log(
	symbol: str,
	price: float,
	is_anomaly: bool,
	z_score: float,
	alert_triggered: bool,
	reason: str,
) -> None:
	"""Save one monitoring event to the database.

	Args:
		symbol: Instrument symbol being monitored.
		price: Observed instrument price.
		is_anomaly: Whether the observation was anomalous.
		z_score: Calculated z-score for the observation.
		alert_triggered: Whether an alert was triggered.
		reason: Explanation for the anomaly or alert state.
	"""
	init_db()
	reason = str(reason)
	with sqlite3.connect(DATABASE_PATH) as connection:
		connection.execute(
			"""
			INSERT INTO logs (
				timestamp, symbol, price, is_anomaly, z_score,
				alert_triggered, reason
			) VALUES (?, ?, ?, ?, ?, ?, ?)
			""",
			(
				datetime.now(),
				symbol,
				price,
				int(is_anomaly),
				z_score,
				int(alert_triggered),
				reason,
			),
		)


def get_recent_logs(limit: int = 50) -> pd.DataFrame:
	"""Return the most recent monitoring logs as a pandas DataFrame.

	Args:
		limit: Maximum number of records to return.

	Returns:
		A DataFrame containing the most recent logs, newest first.

	Raises:
		ValueError: If ``limit`` is less than one.
	"""
	if limit < 1:
		raise ValueError("limit must be at least 1")

	init_db()
	with sqlite3.connect(DATABASE_PATH) as connection:
		return pd.read_sql_query(
			"SELECT * FROM logs ORDER BY timestamp DESC, id DESC LIMIT ?",
			connection,
			params=(limit,),
		)
