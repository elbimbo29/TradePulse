import streamlit as st

from main import run_pipeline


st.set_page_config(page_title="TradePulse Monitor", page_icon="📈", layout="wide")
st.title("TradePulse Multi-Agent Monitoring")
st.caption("Monitor pipeline results, price thresholds, and historical market activity.")

with st.sidebar:
	st.header("Pipeline Settings")
	stock_symbol = st.text_input("Stock Symbol", value="IBM").strip().upper()
	min_threshold = st.number_input("Min Threshold Price", min_value=0.0, value=0.0, step=0.01)
	max_threshold = st.number_input("Max Threshold Price", min_value=0.0, value=0.0, step=0.01)
	api_key = st.text_input("API Key", type="password")
	run_pipeline_button = st.button("Run TradePulse Pipeline", type="primary", use_container_width=True)


def _first(result, *keys, default=None):
	"""Read a value from a pipeline result without requiring one result schema."""
	if not isinstance(result, dict):
		return default
	for key in keys:
		if key in result:
			return result[key]
	return default


if run_pipeline_button:
	if not stock_symbol:
		st.error("Enter a stock symbol.")
	elif max_threshold and min_threshold > max_threshold:
		st.error("Minimum threshold must not exceed maximum threshold.")
	else:
		try:
			with st.spinner("Running TradePulse pipeline..."):
				result = run_pipeline(
					stock_symbol,
					min_threshold=min_threshold,
					max_threshold=max_threshold,
					api_key=api_key,
				)

			st.subheader(f"{stock_symbol} Metrics")
			metrics = _first(result, "metrics", "stock_metrics", default={})
			if not isinstance(metrics, dict):
				metrics = {}
			metric_values = list(metrics.items())
			if metric_values:
				columns = st.columns(min(len(metric_values), 4))
				for column, (label, value) in zip(columns, metric_values):
					column.metric(str(label).replace("_", " ").title(), value)
			else:
				st.info("No stock metrics were returned.")

			alerts = _first(result, "alerts", "notifications", "warnings", default=[])
			if isinstance(alerts, str):
				alerts = [alerts]
			for alert in alerts or []:
				st.warning(alert)

			history = _first(result, "historical_prices", "history", "prices", default=None)
			if history is not None:
				st.subheader("Historical Prices")
				st.line_chart(history)
			else:
				st.info("No historical price data was returned.")
		except Exception as exc:
			st.error(f"Pipeline failed: {exc}")
