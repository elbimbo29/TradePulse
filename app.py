# ========================================== 
# Imports
# ==========================================
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
from main import run_pipeline
import os
from dotenv import load_dotenv

# Load environment variables from a .env file before running the app.
load_dotenv()
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

# Cache the CSV export for sentiment logs so the app can reuse the generated output
@st.cache_data
def sentiment_logs_to_csv(df):
    """Convert a DataFrame into CSV bytes for download."""
    return df.to_csv(index=False).encode("utf-8")


# ========================================== 
# App Setup
# ==========================================
st.set_page_config(page_title="TradePulse Monitor", page_icon="📈", layout="wide")
st.title("TradePulse Multi-Agent Monitoring")
st.caption("Monitor pipeline results, price thresholds, and historical market activity.")

# Store default minimum and maximum threshold values in session state
if "min_price" not in st.session_state:
    st.session_state.min_price = 100.0
if "max_price" not in st.session_state:
    st.session_state.max_price = 150.0


def adjust_max_price():
    # Keep the maximum price above the minimum price to avoid invalid threshold ranges.
    if st.session_state.min_price >= st.session_state.max_price:
        st.session_state.max_price = st.session_state.min_price + 50.0


# ========================================== 
# Sidebar Controls
# ==========================================
with st.sidebar:
    st.header("Pipeline Settings")
    stock_symbol = st.text_input("Stock Symbol", "IBM").strip().upper()
    min_threshold = st.number_input(
        "Min Threshold Price",
        min_value=0.0,
        step=0.01,
        key="min_price",
        on_change=adjust_max_price,
    )
    max_threshold = st.number_input("Max Threshold Price", min_value=0.0, step=0.01, key="max_price")
    api_key = st.text_input(
        "Finnhub API Key",
        value=os.getenv("FINNHUB_API_KEY", ""),
        type="password",
    )
    thresholds_invalid = min_threshold > max_threshold
    if thresholds_invalid:
        st.sidebar.error("⚠️ Minimum threshold must not exceed maximum threshold.")

# Create the three main tabs in the dashboard interface.
tab1, tab2, tab3 = st.tabs([
    "🚀 Manual Pipeline Trigger",
    "📊 Live Database Log & Trends",
    "🤖 Market News Sentiment Analytics",
])

# ========================================== 
# Tab 1: Manual Pipeline Trigger
# ==========================================
with tab1:
    if st.button("Run TradePulse Pipeline", type="primary", disabled=thresholds_invalid):
        if not stock_symbol:
            st.error("Enter a stock symbol.")
        elif max_threshold and min_threshold > max_threshold:
            st.error("Minimum threshold must not exceed maximum threshold.")
        else:
            try:
                symbol = stock_symbol
                min_price = float(min_threshold)
                max_price = float(max_threshold)
                rules = {symbol: {"min": min_price, "max": max_price}}
                
                with st.spinner("Running TradePulse pipeline..."):
                    result = run_pipeline(symbol=symbol, rules=rules, api_key=api_key)
                
                st.session_state["pipeline_output"] = result
                st.rerun()  # Forces immediate redraw so output is displayed instantly
            except Exception as exc:
                st.error(f"Pipeline failed: {exc}")

    # Display persistent pipeline output from session state if available
    if "pipeline_output" in st.session_state:
        st.success("Pipeline output is available.")
        data = st.session_state["pipeline_output"]
        if isinstance(data, dict):
            metrics = data.get("metrics", data.get("stock_metrics", {}))
            metrics = metrics if isinstance(metrics, dict) else {}
            value_for = lambda *keys: next(
                (metrics[key] for key in keys if key in metrics),
                next((data[key] for key in keys if key in data), "N/A"),
            )
            metric_values = [
                ("Stock Symbol", value_for("symbol", "stock_symbol") or stock_symbol),
                ("Fetched Price", value_for("price", "stock_price", "fetched_price", "close")),
                ("Volume", value_for("volume", "stock_volume")),
            ]
            
            for column, (label, value) in zip(st.columns(3), metric_values):
                column.metric(label, value)

            if data.get("alert_triggered") is True:
                alert_reason = data.get("alert_reason", data.get("reason", "Price outside limits."))
                st.error(f"Alert triggered: {alert_reason}")
            elif data.get("alert_triggered") is False:
                st.success("✅ Price within limits / Normal operation.")
            else:
                st.info("Pipeline completed successfully.")

            sentiment = data.get("sentiment_analysis")
            if isinstance(sentiment, dict):
                overall = str(
                    sentiment.get("overall_sentiment")
                    or sentiment.get("sentiment")
                    or "NEUTRAL"
                ).upper()
                article_count = sentiment.get("articles_analyzed", sentiment.get("article_count", 0))
                summary = (
                    sentiment.get("analysis")
                    or sentiment.get("summary")
                    or sentiment.get("ai_summary")
                    or sentiment.get("market_diagnosis")
                    or "No AI summary was returned."
                )
                with st.expander("🤖 AI News Sentiment & Market Diagnosis", expanded=True):
                    left, right = st.columns(2)
                    left.metric("Overall sentiment", overall)
                    left.caption(f"{article_count} articles analyzed")
                    if overall == "BULLISH":
                        right.success(summary)
                    elif overall == "BEARISH":
                        right.error(summary)
                    else:
                        right.info(summary)
            
            # Render the automated financial disclaimer injected from the backend pipeline gateway layer
            if "disclaimer" in data:
                st.caption(f"⚠️ *{data['disclaimer']}*")
                
            st.json(st.session_state["pipeline_output"])

# ========================================== 
# Tab 2: Live Database Log & Trends
# ==========================================
with tab2:
    enable_live_refresh = st.toggle("🔄 Enable Live Auto-Refresh", value=True)
    if enable_live_refresh:
        refresh_count = st_autorefresh(interval=5000, limit=None, key="db_chart_autorefresh")
        st.caption(f"Live refresh: ACTIVE · Refresh count: {refresh_count}")
    else:
        st.caption("Live refresh: PAUSED")
        
    if st.button("Refresh Database Logs"):
        st.rerun()
        
    try:
        with sqlite3.connect("tradepulse.db") as connection:
            df = pd.read_sql_query("SELECT * FROM logs", connection)
            price_logs = pd.read_sql_query("SELECT * FROM price_logs", connection)
            
        if df.empty:
            st.info("No monitoring logs found in database yet. Run the pipeline to record data.")
        else:
            anomaly = next((c for c in df.columns if "anomal" in c.lower()), None)
            alert = next((c for c in df.columns if "alert" in c.lower()), None)
            anomaly_count = int(df[anomaly].fillna(False).astype(bool).sum()) if anomaly else 0
            alert_count = int(df[alert].fillna(False).astype(bool).sum()) if alert else 0
            
            cards = st.columns(3)
            cards[0].metric("Total Logs", len(df))
            cards[1].metric("Anomaly Count", anomaly_count)
            cards[2].metric("Alert Count", alert_count)
            
            if not price_logs.empty and {"timestamp", "price", "symbol"}.issubset(price_logs.columns):
                selected_symbol_tab2 = st.selectbox(
                    "Filter price history by symbol",
                    sorted(price_logs["symbol"].dropna().astype(str).unique()),
                    key="tab2_symbol_select"
                )
                df_filtered = price_logs[price_logs["symbol"].astype(str) == selected_symbol_tab2].copy()
                df_filtered["timestamp"] = pd.to_datetime(df_filtered["timestamp"], errors="coerce")
                df_filtered["price"] = pd.to_numeric(df_filtered["price"], errors="coerce")
                df_filtered = df_filtered.dropna(subset=["timestamp", "price"])
                
                if not df_filtered.empty:
                    if "is_anomaly" in df_filtered.columns:
                        df_anomalies = df_filtered[df_filtered["is_anomaly"].fillna(False).astype(bool)]
                    else:
                        df_anomalies = df_filtered.iloc[0:0]
                        
                    z_score_column = next(
                        (column for column in ("z_score", "zscore", "z-score") if column in df_filtered.columns),
                        None,
                    )
                    if z_score_column is None:
                        df_filtered["z_score"] = "N/A"
                        z_score_column = "z_score"
                        
                    fig = px.line(
                        df_filtered,
                        x="timestamp",
                        y="price",
                        markers=True,
                        custom_data=[z_score_column],
                    )
                    fig.update_traces(
                        hovertemplate="Timestamp: %{x}<br>Price: %{y}<br>Z-score: %{customdata[0]}<extra></extra>"
                    )
                    fig.add_scatter(
                        x=df_anomalies["timestamp"],
                        y=df_anomalies["price"],
                        mode="markers",
                        marker=dict(color="red", size=12, symbol="x"),
                        name="Anomaly Detected",
                        customdata=df_anomalies[[z_score_column]],
                        hovertemplate="Timestamp: %{x}<br>Price: %{y}<br>Z-score: %{customdata[0]}<extra></extra>",
                    )
                    fig.add_hline(y=min_threshold, line_dash="dash", line_color="red")
                    fig.add_hline(y=max_threshold, line_dash="dash", line_color="red")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No valid price history is available for the selected symbol.")
            else:
                st.info("No price logs found in the database.")
                
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Export Logs to CSV",
                data=csv_data,
                file_name="tradepulse_monitoring_logs.csv",
                mime="text/csv",
            )
            st.dataframe(df)
            
    except Exception as exc:
        st.error(f"Unable to load database logs: {exc}")

# ========================================== 
# Tab 3: Market News Sentiment Analytics
# ==========================================
with tab3:
    try:
        with sqlite3.connect("tradepulse.db") as connection:
            df_sentiment = pd.read_sql_query(
                "SELECT timestamp, symbol, price, alert_triggered, sentiment, summary "
                "FROM sentiment_logs",
                connection,
            )
        if df_sentiment.empty:
            st.warning("⚠️ No sentiment ratings are available in the database logs yet.")
            st.caption("Run the pipeline with news sentiment enabled to populate these logs.")
        else:
            st.dataframe(df_sentiment, use_container_width=True)
            st.download_button(
                "📥 Export Sentiment Logs to CSV",
                data=sentiment_logs_to_csv(df_sentiment),
                file_name="tradepulse_sentiment_logs.csv",
                mime="text/csv",
            )
            distribution = df_sentiment["sentiment"].astype(str).str.upper().value_counts()
            chart_column, metrics_column = st.columns([3, 1])
            with chart_column:
                st.bar_chart(distribution.rename("Articles"))
            with metrics_column:
                st.metric("Analyzed articles", int(distribution.sum()))
                st.metric("Most common", distribution.idxmax())
                st.metric("Sentiment types", len(distribution))
    except (sqlite3.Error, pd.errors.DatabaseError) as exc:
        st.warning("⚠️ No sentiment ratings are available in the database logs yet.")
        st.caption("Run the pipeline with news sentiment enabled to create and populate the sentiment logs.")