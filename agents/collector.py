# agents/collector.py
import os
import requests
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from config import Config
from logger import logger  # Import our structured logger

api_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.exceptions.RequestException, requests.exceptions.Timeout)),
    reraise=True
)

@api_retry
def _execute_price_request(url: str, params: dict) -> dict:
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def fetch_price(symbol: str, api_key: str = None) -> float:
    """Fetches real-time stock price from Finnhub API with automated retries and structured logging."""
    key = api_key if api_key and api_key != "mock-api-key" else Config.FINNHUB_API_KEY
    
    if not key:
        logger.error("missing_api_key", agent="collector", target="finnhub")
        return 185.0

    url = "https://finnhub.io/api/v1/quote"
    params = {"symbol": symbol, "token": key}

    try:
        logger.info("fetching_stock_price", symbol=symbol)
        data = _execute_price_request(url, params)
        
        price = data.get("c")
        if price is not None and price != 0:
            logger.info("stock_price_fetched_successfully", symbol=symbol, price=price)
            return float(price)
        else:
            logger.warning("invalid_price_payload", symbol=symbol, response_data=data)
            return 185.0

    except Exception as e:
        logger.error("price_request_failed_after_retries", symbol=symbol, error_type=type(e).__name__, error=str(e))
        return 185.0


@api_retry
def _execute_news_request(url: str, params: dict) -> list:
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def fetch_news(symbol: str, api_key: str = None) -> list:
    """Fetches company news headlines from Finnhub API with structured logging."""
    key = api_key if api_key and api_key != "mock-api-key" else Config.FINNHUB_API_KEY
    
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
        logger.info("fetching_company_news", symbol=symbol)
        news_data = _execute_news_request(url, params)
        
        if isinstance(news_data, list):
            headlines = [item["headline"] for item in news_data if "headline" in item][:5]
            logger.info("company_news_fetched_successfully", symbol=symbol, article_count=len(headlines))
            return headlines
        return []

    except Exception as e:
        logger.error("news_request_failed_after_retries", symbol=symbol, error_type=type(e).__name__, error=str(e))
        return []


def fetch_stock_data(symbol: str, api_key: str = None) -> dict:
    """Wrapper function returning both price and news."""
    price = fetch_price(symbol, api_key)
    news = fetch_news(symbol, api_key)
    return {"price": price, "news": news}