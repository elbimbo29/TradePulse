def evaluate_thresholds(price: float, symbol: str, rules: dict) -> dict:
	"""Evaluate a price against the configured thresholds for a symbol.

	Args:
		price: The current price to evaluate.
		symbol: The symbol whose thresholds should be used.
		rules: A mapping of symbols to ``min`` and ``max`` values.

	Returns:
		A dictionary with ``triggered``, ``reason``, and ``price`` keys.
	"""
	symbol_rules = rules.get(symbol, {})
	minimum = symbol_rules.get("min")
	maximum = symbol_rules.get("max")

	if minimum is not None and price < minimum:
		reason = "below_min"
		triggered = True
	elif maximum is not None and price > maximum:
		reason = "above_max"
		triggered = True
	else:
		reason = None
		triggered = False

	return {"triggered": triggered, "reason": reason, "price": float(price)}
