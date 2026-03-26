"""Tests for the stock module."""

import pandas as pd
import numpy as np

from magicglass.stock import compute_trend_summary, format_trend_report


def _make_hist(num_days=60, start_price=100.0, end_price=120.0):
    """Helper to create a fake stock history DataFrame."""
    dates = pd.date_range(start="2025-01-01", periods=num_days, freq="B")
    prices = np.linspace(start_price, end_price, num_days)
    return pd.DataFrame(
        {
            "Open": prices - 1,
            "High": prices + 2,
            "Low": prices - 2,
            "Close": prices,
            "Volume": np.random.randint(1_000_000, 10_000_000, size=num_days),
        },
        index=dates,
    )


class TestComputeTrendSummary:
    def test_basic_uptrend(self):
        hist = _make_hist(60, 100.0, 120.0)
        summary = compute_trend_summary(hist)

        assert summary["current_price"] > summary["period_start_price"]
        assert summary["price_change"] > 0
        assert summary["price_change_pct"] > 0
        assert summary["high_52w"] > 0
        assert summary["low_52w"] > 0
        assert summary["avg_volume"] > 0

    def test_basic_downtrend(self):
        hist = _make_hist(60, 120.0, 80.0)
        summary = compute_trend_summary(hist)

        assert summary["current_price"] < summary["period_start_price"]
        assert summary["price_change"] < 0
        assert summary["price_change_pct"] < 0

    def test_sma_present_for_enough_data(self):
        hist = _make_hist(60, 100.0, 110.0)
        summary = compute_trend_summary(hist)

        assert summary["sma_20"] is not None
        assert summary["sma_50"] is not None

    def test_sma_none_for_insufficient_data(self):
        hist = _make_hist(10, 100.0, 105.0)
        summary = compute_trend_summary(hist)

        assert summary["sma_20"] is None
        assert summary["sma_50"] is None

    def test_empty_input(self):
        summary = compute_trend_summary(None)
        assert summary == {}

        empty_df = pd.DataFrame()
        summary = compute_trend_summary(empty_df)
        assert summary == {}


class TestFormatTrendReport:
    def test_format_with_data(self):
        summary = {
            "current_price": 120.0,
            "period_start_price": 100.0,
            "price_change": 20.0,
            "price_change_pct": 20.0,
            "high_52w": 130.0,
            "low_52w": 90.0,
            "avg_volume": 5_000_000,
            "sma_20": 115.0,
            "sma_50": 110.0,
        }
        report = format_trend_report("BABA", summary)
        assert "BABA" in report
        assert "$120.00" in report
        assert "UPTREND" in report

    def test_format_downtrend(self):
        summary = {
            "current_price": 80.0,
            "period_start_price": 100.0,
            "price_change": -20.0,
            "price_change_pct": -20.0,
            "high_52w": 110.0,
            "low_52w": 75.0,
            "avg_volume": 3_000_000,
            "sma_20": 85.0,
            "sma_50": 90.0,
        }
        report = format_trend_report("BABA", summary)
        assert "DOWNTREND" in report

    def test_format_no_data(self):
        report = format_trend_report("UNKNOWN", {})
        assert "No data" in report
