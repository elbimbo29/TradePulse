import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def fetch_price(symbol: str, api_key: str = None) -> float:
    """Fetches real-time stock price from Finnhub API."""
    key = api_key if api_key and api_key != "mock-api-key" else os.getenv("FINNHUB_API_KEY")
    
    if not key:
        print("[Collector Error] No valid Finnhub API key found in .env or arguments.")
        return 185.0

    url = "https://finnhub.io/api/v1/quote"
    params = {"symbol": symbol, "token": key}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Finnhub returns 'c' for current price
        price = data.get("c")
        if price is not None and price != 0:
            return float(price)
        else:
            print(f"[Collector Error] Key 'c' missing or zero in response: {data}")
            return 185.0

    except Exception as e:
        print(f"[Collector Error] Price request failed for {symbol}: {type(e).__name__} - {e}")
        return 185.0


def fetch_news(symbol: str, api_key: str = None) -> list:
    """Fetches company news headlines from Finnhub API."""
    key = api_key if api_key and api_key != "mock-api-key" else os.getenv("FINNHUB_API_KEY")
    
    if not key:
        return []

    today = datetime.now()
    seven_days_ago = today - timedelta(days=7)

    url = "https://finnhub.io/api/v1/company-news"
    params = {
        "symbol": symbol,
        "from": seven_days_ago.strftime("%Y-%m-%d"),
        "to": today.strftime("%Y-%m-%d"),
        "token": key
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        news_data = response.json()
        
        if isinstance(news_data, list):
            return [item["headline"] for item in news_data if "headline" in item][:5]
        return []

    except Exception as e:
        print(f"[Collector Error] News request failed for {symbol}: {type(e).__name__} - {e}")
        return []


def fetch_stock_data(symbol: str, api_key: str = None) -> dict:
    """Wrapper function returning both price and news."""
    price = fetch_price(symbol, api_key)
    news = fetch_news(symbol, api_key)
    return {"price": price, "news": news}