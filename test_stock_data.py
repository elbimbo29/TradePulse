# test_stock_data.py
import pytest
from my_agent.tools import fetch_stock_price, validate_price_thresholds

def test_fetch_stock_price_schema():
    """Ensure API parser returns expected data types and keys."""
    data = fetch_stock_price("IBM")
    assert "symbol" in data
    assert "price" in data
    assert isinstance(data["price"], float)
    assert data["price"] > 0.0

def test_price_threshold_logic():
    """Test deterministic alert boundaries."""
    rules = {"IBM": {"min": 100.0, "max": 150.0}}
    # Price inside limits
    assert validate_price_thresholds("IBM", 120.0, rules) is False
    # Price breaching max threshold (triggers alert)
    assert validate_price_thresholds("IBM", 155.0, rules) is True