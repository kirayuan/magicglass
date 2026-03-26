"""Tests for fundamental analysis module."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.magicglass.analysis.fundamental import (
    FundamentalResult,
    analyse_fundamentals,
    score_debt_to_equity,
    score_pe_ratio,
    score_profit_margins,
    score_revenue_growth,
    score_roe,
)


class TestScorePeRatio:
    def test_none(self):
        assert score_pe_ratio(None) == 0.3

    def test_negative(self):
        assert score_pe_ratio(-5.0) == 0.3

    def test_deep_value(self):
        assert score_pe_ratio(10.0) == 1.0

    def test_moderate(self):
        assert score_pe_ratio(20.0) == 0.7

    def test_high(self):
        assert score_pe_ratio(35.0) == 0.5

    def test_very_high(self):
        assert score_pe_ratio(50.0) == 0.3


class TestScoreRevenueGrowth:
    def test_none(self):
        assert score_revenue_growth(None) == 0.3

    def test_high_growth(self):
        assert score_revenue_growth(0.35) == 1.0

    def test_moderate_growth(self):
        assert score_revenue_growth(0.20) == 0.7

    def test_low_growth(self):
        assert score_revenue_growth(0.05) == 0.5

    def test_negative_growth(self):
        assert score_revenue_growth(-0.10) == 0.2


class TestScoreProfitMargins:
    def test_none(self):
        assert score_profit_margins(None) == 0.3

    def test_high_margins(self):
        assert score_profit_margins(0.30) == 1.0

    def test_moderate_margins(self):
        assert score_profit_margins(0.15) == 0.7

    def test_low_margins(self):
        assert score_profit_margins(0.05) == 0.5

    def test_negative_margins(self):
        assert score_profit_margins(-0.05) == 0.2


class TestScoreDebtToEquity:
    def test_none(self):
        assert score_debt_to_equity(None) == 0.3

    def test_low_debt(self):
        assert score_debt_to_equity(20.0) == 1.0

    def test_moderate_debt(self):
        assert score_debt_to_equity(50.0) == 0.7

    def test_high_debt(self):
        assert score_debt_to_equity(120.0) == 0.5

    def test_very_high_debt(self):
        assert score_debt_to_equity(200.0) == 0.3


class TestScoreRoe:
    def test_none(self):
        assert score_roe(None) == 0.3

    def test_high_roe(self):
        assert score_roe(0.30) == 1.0

    def test_moderate_roe(self):
        assert score_roe(0.20) == 0.7

    def test_low_roe(self):
        assert score_roe(0.08) == 0.5

    def test_very_low_roe(self):
        assert score_roe(0.02) == 0.3


class TestAnalyseFundamentals:
    def test_strong_fundamentals(self):
        info = {
            "trailingPE": 12.0,
            "revenueGrowth": 0.35,
            "profitMargins": 0.30,
            "debtToEquity": 20.0,
            "returnOnEquity": 0.30,
        }
        result = analyse_fundamentals("TEST", info)
        assert isinstance(result, FundamentalResult)
        assert result.ticker == "TEST"
        assert result.overall_score == 1.0
        assert "bullish" in result.summary.lower()

    def test_weak_fundamentals(self):
        info = {
            "trailingPE": 60.0,
            "revenueGrowth": -0.10,
            "profitMargins": -0.05,
            "debtToEquity": 200.0,
            "returnOnEquity": 0.02,
        }
        result = analyse_fundamentals("TEST", info)
        assert result.overall_score < 0.5
        assert "bearish" in result.summary.lower()

    def test_empty_info(self):
        result = analyse_fundamentals("TEST", {})
        assert result.overall_score == 0.3  # all None → 0.3
        assert result.ticker == "TEST"

    def test_partial_info(self):
        info = {"trailingPE": 20.0}
        result = analyse_fundamentals("TEST", info)
        assert isinstance(result, FundamentalResult)
        assert len(result.scores) == 5
