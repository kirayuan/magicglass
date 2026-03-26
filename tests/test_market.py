"""Tests for market / technical analysis module."""

import numpy as np
import pandas as pd

from magicglass.analysis.market import (
    MarketResult,
    analyse_market,
    compute_ema,
    compute_macd,
    compute_rsi,
    compute_sma,
    score_bollinger,
    score_ma_crossover,
    score_macd,
    score_rsi,
    score_volume_trend,
)


def _make_price_series(start: float, end: float, n: int = 100) -> pd.Series:
    """Create a linearly spaced price series."""
    return pd.Series(np.linspace(start, end, n))


def _make_dataframe(
    close_start: float = 100.0,
    close_end: float = 120.0,
    n: int = 100,
) -> pd.DataFrame:
    """Create a simple OHLCV dataframe for testing."""
    close = np.linspace(close_start, close_end, n)
    return pd.DataFrame(
        {
            "Open": close * 0.99,
            "High": close * 1.02,
            "Low": close * 0.98,
            "Close": close,
            "Volume": np.random.randint(1_000_000, 10_000_000, size=n),
        }
    )


class TestComputeSma:
    def test_basic(self):
        series = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        sma = compute_sma(series, 3)
        assert len(sma) == 5
        assert abs(sma.iloc[-1] - 4.0) < 0.01


class TestComputeEma:
    def test_basic(self):
        series = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        ema = compute_ema(series, 3)
        assert len(ema) == 5
        # EMA should be close to SMA for simple monotonic series
        assert ema.iloc[-1] > 3.0


class TestComputeRsi:
    def test_uptrend(self):
        series = _make_price_series(100, 150, 50)
        rsi = compute_rsi(series)
        # Strong uptrend should have high RSI
        assert rsi.iloc[-1] > 70

    def test_downtrend(self):
        series = _make_price_series(150, 100, 50)
        rsi = compute_rsi(series)
        # Strong downtrend should have low RSI
        assert rsi.iloc[-1] < 30


class TestComputeMacd:
    def test_basic(self):
        series = _make_price_series(100, 120, 50)
        macd_line, signal_line = compute_macd(series)
        assert len(macd_line) == 50
        assert len(signal_line) == 50


class TestScoreMaCrossover:
    def test_bullish(self):
        # Uptrend: short MA above long MA
        close = _make_price_series(100, 150, 100)
        score = score_ma_crossover(close)
        assert score == 1.0

    def test_bearish(self):
        # Downtrend: short MA below long MA
        close = _make_price_series(150, 100, 100)
        score = score_ma_crossover(close)
        assert score == 0.0


class TestScoreRsi:
    def test_oversold(self):
        close = _make_price_series(150, 100, 50)
        score = score_rsi(close)
        assert score > 0.5  # oversold = bullish

    def test_overbought(self):
        close = _make_price_series(100, 150, 50)
        score = score_rsi(close)
        assert score < 0.5  # overbought = bearish


class TestScoreMacd:
    def test_bullish_histogram(self):
        close = _make_price_series(100, 150, 50)
        score = score_macd(close)
        assert score == 0.8

    def test_bearish_histogram(self):
        close = _make_price_series(150, 100, 50)
        score = score_macd(close)
        assert score == 0.2


class TestScoreVolumeTrend:
    def test_low_volume(self):
        volume = pd.Series([1_000_000] * 25)
        score = score_volume_trend(volume)
        # Flat volume → neutral-ish
        assert 0.3 <= score <= 0.7

    def test_insufficient_data(self):
        volume = pd.Series([1_000_000] * 5)
        score = score_volume_trend(volume, window=20)
        assert score == 0.5

    def test_empty_volume(self):
        volume = pd.Series(dtype=float)
        assert score_volume_trend(volume) == 0.5


class TestScoreBollinger:
    def test_returns_valid_range(self):
        close = _make_price_series(100, 120, 50)
        score = score_bollinger(close)
        assert 0.0 <= score <= 1.0


class TestAnalyseMarket:
    def test_uptrend(self):
        df = _make_dataframe(100, 150, 100)
        result = analyse_market("TEST", df)
        assert isinstance(result, MarketResult)
        assert result.ticker == "TEST"
        assert 0.0 <= result.overall_score <= 1.0
        assert "rsi" in result.indicators
        assert "macd" in result.indicators

    def test_downtrend(self):
        df = _make_dataframe(150, 100, 100)
        result = analyse_market("TEST", df)
        assert 0.0 <= result.overall_score <= 1.0

    def test_empty_dataframe(self):
        result = analyse_market("TEST", pd.DataFrame())
        assert result.summary == "Insufficient data"
        assert result.overall_score == 0.5

    def test_missing_close_column(self):
        df = pd.DataFrame({"Open": [1, 2, 3]})
        result = analyse_market("TEST", df)
        assert result.summary == "Insufficient data"
