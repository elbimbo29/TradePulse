"""Continuously run the stock-price monitoring pipeline in the background."""

import json
import os
import time
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

from main import run_pipeline

WATCHLIST = ["IBM", "AAPL", "TSLA", "MSFT"]
THRESHOLD_RULES = {
    "IBM": {"min": 100, "max": 200},
    "AAPL": {"min": 150, "max": 250},
    "TSLA": {"min": 100, "max": 300},
    "MSFT": {"min": 300, "max": 500},
}


def _status(message: str) -> None:
	print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {message}", flush=True)


def scheduled_job() -> None:
	"""Run one monitoring check for every ticker in the watchlist."""
	try:
		price_history = json.loads(os.getenv("PRICE_HISTORY", "[]"))
		if not isinstance(price_history, list):
			raise ValueError("PRICE_HISTORY must be a JSON array")
	except (TypeError, ValueError, json.JSONDecodeError) as error:
		_status(f'{{"event":"watchlist_failed","error":"{error}"}}')
		return

	api_key = os.getenv("API_KEY")
	for symbol in WATCHLIST:
		_status(f'{{"event":"ticker_check_started","symbol":"{symbol}"}}')
		try:
			run_pipeline(symbol, THRESHOLD_RULES[symbol], price_history, api_key)
			_status(f'{{"event":"ticker_check_completed","symbol":"{symbol}"}}')
		except Exception as error:
			_status(
				f'{{"event":"ticker_check_failed","symbol":"{symbol}",'
				f'"error":"{error}"}}'
			)


def main() -> None:
	load_dotenv()
	interval = float(os.getenv("CHECK_INTERVAL_SECONDS", "60"))

	scheduler = BackgroundScheduler()
	scheduler.add_job(
		scheduled_job,
		trigger="interval",
		seconds=interval,
		next_run_time=datetime.now(),
	)
	scheduler.start()
	_status("Background monitor started.")

	try:
		while True:
			time.sleep(1)
	except (KeyboardInterrupt, SystemExit):
		_status("Stopping background monitor.")
		scheduler.shutdown(wait=False)


if __name__ == "__main__":
	main()
