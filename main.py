# main.py
import os
import ast
from dotenv import load_dotenv
from agents.collector import fetch_stock_data
from agents.anomaly import detect_anomaly
from agents.sentiment import analyze_sentiment
from agents.guardrails import validate_input_ticker, enforce_output_guardrails
from database import log_price
from telemetry import setup_telemetry

load_dotenv()

# Initialize the OpenTelemetry tracer on application startup
tracer = setup_telemetry()


def run_pipeline(symbol: str = "IBM", rules: dict = None, **kwargs):
    # Root span tracking the entire multi-agent pipeline execution
    with tracer.start_as_current_span("tradepulse.run_pipeline") as root_span:
        root_span.set_attribute("trade.symbol", symbol)

        # 0. INPUT GUARDRAIL: Validate symbol & prevent injection
        with tracer.start_as_current_span("guardrails.input_validation") as span:
            is_valid, validated_symbol_or_msg = validate_input_ticker(symbol)
            span.set_attribute("guardrail.input_passed", is_valid)
            
            if not is_valid:
                span.set_attribute("guardrail.error", validated_symbol_or_msg)
                print(f"[GUARDRAIL BLOCKED]: {validated_symbol_or_msg}")
                return {
                    "status": "blocked",
                    "error": validated_symbol_or_msg,
                    "symbol": symbol
                }
            
            # Use the clean, sanitized symbol downstream
            clean_symbol = validated_symbol_or_msg

        # 1. Fetch live stock data & news from Finnhub
        with tracer.start_as_current_span("agent.collector") as span:
            stock_data = fetch_stock_data(clean_symbol)
            price = stock_data.get("price", 185.0)
            news = stock_data.get("news", [])
            span.set_attribute("stock.price", price)
            span.set_attribute("news.count", len(news))

        # 2. Check for anomalies (passing rules)
        with tracer.start_as_current_span("agent.anomaly") as span:
            anomaly_result = detect_anomaly(clean_symbol, price, rules=rules)
            span.set_attribute("anomaly.triggered", anomaly_result.get("is_anomaly", False))

        # 3. Perform AI Sentiment Analysis using OpenAI
        with tracer.start_as_current_span("agent.sentiment") as span:
            sentiment_result = analyze_sentiment(clean_symbol, news)
            span.set_attribute("sentiment.rating", sentiment_result.get("sentiment", "NEUTRAL"))

        # 4. OUTPUT GUARDRAIL: Enforce compliance & sanitize LLM output
        with tracer.start_as_current_span("guardrails.output_compliance") as span:
            raw_summary = sentiment_result.get("analysis", "")
            sanitized_summary = enforce_output_guardrails(raw_summary)
            # Update sentiment dict with sanitized output
            sentiment_result["analysis"] = sanitized_summary
            span.set_attribute("guardrail.output_sanitized", True)

        # 5. Construct record and log to SQLite database
        with tracer.start_as_current_span("database.log_price") as span:
            alert_triggered = anomaly_result.get("is_anomaly", False)
            reason = anomaly_result.get("reason", "Normal operation")

            log_price(
                symbol=clean_symbol,
                price=price,
                anomaly_metrics=str(anomaly_result),
                alert_triggered=alert_triggered,
                reason=reason,
                sentiment=sentiment_result.get("sentiment", "NEUTRAL"),
                summary=sanitized_summary
            )
            span.set_attribute("db.log_success", True)

        output = {
            "symbol": clean_symbol,
            "price": price,
            "alert_triggered": alert_triggered,
            "reason": reason,
            "sentiment_analysis": sentiment_result,
        }

        print(output)
        return output


if __name__ == "__main__":
    # Test 1: Valid Execution
    print("--- Running Valid Input ---")
    run_pipeline("IBM")

    # Test 2: Invalid / Injection Input (Guardrail Blocked)
    print("\n--- Running Guardrail Block Test ---")
    run_pipeline("IBM; DROP TABLE users;")