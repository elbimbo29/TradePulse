import numpy as np


def detect_anomaly(symbol, price, rules=None):
    is_anomaly = False
    reason = "Normal operation"
    
    # Check strict user-defined threshold rules from sidebar
    if rules and symbol in rules:
        min_limit = rules[symbol].get("min", 0.0)
        max_limit = rules[symbol].get("max", float("inf"))
        
        if price < min_limit:
            return {
                "is_anomaly": True,
                "reason": f"Price ${price} is below minimum threshold (${min_limit})"
            }
        elif price > max_limit:
            return {
                "is_anomaly": True,
                "reason": f"Price ${price} is above maximum threshold (${max_limit})"
            }
            
    # Fallback to standard statistical/z-score logic if within limits
    # (Keep your existing rolling-window or z-score calculation here)
    
    return {
        "is_anomaly": is_anomaly,
        "reason": reason
    }