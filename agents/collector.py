import requests


def fetch_stock_data(symbol: str, api_key: str) -> dict:
	"""Fetch the latest stock quote from Alpha Vantage.

	Args:
		symbol: Stock ticker symbol.
		api_key: Alpha Vantage API key.

	Returns:
		A dictionary containing ``symbol``, ``price``, and ``volume``, or
		``None`` when the request or API response is unsuccessful.
	"""
	try:
		response = requests.get(
			"https://www.alphavantage.co/query",
			params={
				"function": "GLOBAL_QUOTE",
				"symbol": symbol,
				"apikey": api_key,
			},
			timeout=10,
		)
		response.raise_for_status()
		data = response.json()
		quote = data.get("Global Quote")

		if not isinstance(quote, dict) or "Note" in data or "Error Message" in data:
			return None

		return {
			"symbol": quote["01. symbol"],
			"price": float(quote["05. price"]),
			"volume": int(quote["06. volume"]),
		}
	except (requests.RequestException, ValueError, KeyError, TypeError):
		return None

if __name__ == "__main__":
    # Quick local test
    print(fetch_stock_data("AAPL", "demo"))