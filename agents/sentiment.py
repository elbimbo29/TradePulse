# agents/sentiment.py
import os
import json
import logging
import datetime
import requests
from typing import Dict, Any, List
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
client = OpenAI()
logger = logging.getLogger(__name__)
DEFAULT_ANALYSIS = "Stock remains within normal operating parameters. AI sentiment summary is standing by for active alert triggers."

def fetch_recent_news(symbol: str, days_back: int = 2) -> List[Dict[str, str]]:
    """
    Fetches company news from Finnhub API for a given symbol.
    """
    if not FINNHUB_API_KEY:
        print("[SentimentAgent] Warning: FINNHUB_API_KEY not set. Using fallback headlines.")
        return [
            {"headline": f"Unusual volume detected in {symbol} stock", "summary": "Market analysts note high volume spike."},
            {"headline": f"{symbol} earnings report released", "summary": "Company reported recent operational changes."}
        ]

    today = datetime.date.today()
    from_date = (today - datetime.timedelta(days=days_back)).strftime('%Y-%m-%d')
    to_date = today.strftime('%Y-%m-%d')

    url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from={from_date}&to={to_date}&token={FINNHUB_API_KEY}"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        articles = response.json()
        
        cleaned_news = []
        for item in articles[:5]:  # Take top 5 news articles
            cleaned_news.append({
                "headline": item.get("headline", ""),
                "summary": item.get("summary", ""),
                "source": item.get("source", "")
            })
        return cleaned_news
    except Exception as e:
        print(f"[SentimentAgent] Error fetching news for {symbol}: {e}")
        return []


def analyze_sentiment(symbol: str, news_items: list) -> dict:
    """Analyze the sentiment of supplied news items for a symbol."""
    default_result = {
        "sentiment": "NEUTRAL",
        "analysis": DEFAULT_ANALYSIS,
        "articles_analyzed": len(news_items),
    }

    if not news_items:
        return default_result

    headlines = []
    for item in news_items:
        if isinstance(item, str):
            text = item
        elif isinstance(item, dict):
            text = item.get("headline", "") or item.get("summary", "")
        else:
            text = ""
        if text:
            headlines.append(str(text))

    prompt = f"""Analyze the sentiment of these recent headlines for {symbol}.
Return JSON only with exactly these keys: "sentiment" (one of "BULLISH", "BEARISH", or "NEUTRAL") and "analysis" (a brief analysis string).
Headlines: {json.dumps(headlines)}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a financial market analyst."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )
        result = json.loads(response.choices[0].message.content or "{}")
        sentiment = str(result.get("sentiment", "NEUTRAL")).upper()
        if sentiment not in {"BULLISH", "BEARISH", "NEUTRAL"}:
            sentiment = "NEUTRAL"
        return {
            "sentiment": sentiment,
            "analysis": result.get("analysis") or DEFAULT_ANALYSIS,
            "articles_analyzed": len(news_items),
        }
    except Exception as e:
        logger.warning("OpenAI sentiment analysis failed: %s", e)
        return default_result


def analyze_news_sentiment(symbol: str, trigger_reason: str = "Price Alert") -> Dict[str, Any]:
    """
    Fetches news and queries Gemini/OpenAI to generate a structured sentiment analysis.
    """
    news_items = fetch_recent_news(symbol)

    if not news_items or not trigger_reason:
        return {
            "sentiment": "NEUTRAL",
            "articles_analyzed": len(news_items),
            "analysis": DEFAULT_ANALYSIS
        }

    return analyze_sentiment(symbol, news_items)