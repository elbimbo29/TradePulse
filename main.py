import os
import ast
from dotenv import load_dotenv
from agents.collector import fetch_stock_data
from agents.anomaly import detect_anomaly
from agents.sentiment import analyze_sentiment
from database import log_price

load_dotenv()

def run_pipeline(symbol: str = "IBM", rules: dict = None, **kwargs):
    # 1. Fetch live stock data & news from Finnhub
    stock_data = fetch_stock_data(symbol)
    price = stock_data.get("price", 185.0)
    news = stock_data.get("news", [])

    # 2. Check for anomalies (passing rules)
    anomaly_result = detect_anomaly(symbol, price, rules=rules)

    # 3. Perform AI Sentiment Analysis using OpenAI
    sentiment_result = analyze_sentiment(symbol, news)

    # 4. Construct record and log to SQLite database
    alert_triggered = anomaly_result.get("is_anomaly", False)
    # Pull the exact reason from the anomaly result
    reason = anomaly_result.get("reason", "Normal operation")

    log_price(
        symbol=symbol,
        price=price,
        anomaly_metrics=str(anomaly_result),
        alert_triggered=alert_triggered,
        reason=reason,
        sentiment=sentiment_result.get("sentiment", "NEUTRAL"),
        summary=sentiment_result.get("analysis", "")
    )

    output = {
        "symbol": symbol,
        "price": price,
        "alert_triggered": alert_triggered,
        "reason": reason,
        "sentiment_analysis": sentiment_result
    }
    
    print(output)
    return output

if __name__ == "__main__":
    run_pipeline("IBM")