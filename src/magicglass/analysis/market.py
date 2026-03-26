"""Market / technical analysis module.

Computes common technical indicators from historical OHLCV data and
produces an aggregated market signal in [0, 1] indicating bullish (→1)
or bearish (→0) conditions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

import numpy as np
import pandas as pd

from magicglass.config import (
    LONG_MA_WINDOW,
    MACD_FAST,
    MACD_SIGNAL,
    MACD_SLOW,
    RSI_PERIOD,
    SHORT_MA_WINDOW,
)


@dataclass
class MarketResult:
    """Container for market / technical analysis output."""

    ticker: str
    indicators: Dict[str, float] = field(default_factory=dict)
    signals: Dict[str, float] = field(default_factory=dict)
    overall_score: float = 0.5
    summary: str = ""


# ---------------------------------------------------------------------------
# Technical indicator calculations
# ---------------------------------------------------------------------------

def compute_sma(series: pd.Series, window: int) -> pd.Series:
    """Simple Moving Average."""
    return series.rolling(window=window, min_periods=1).mean()


def compute_ema(series: pd.Series, span: int) -> pd.Series:
    """Exponential Moving Average."""
    return series.ewm(span=span, adjust=False).mean()


def compute_rsi(series: pd.Series, period: int = RSI_PERIOD) -> pd.Series:
    """Relative Strength Index."""
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()
    # When avg_loss is 0 (all gains), RSI should be 100
    # When avg_gain is 0 (all losses), RSI should be 0
    rsi = pd.Series(np.where(
        avg_loss == 0,
        np.where(avg_gain == 0, 50.0, 100.0),
        100.0 - (100.0 / (1.0 + avg_gain / avg_loss)),
    ), index=series.index)
    return rsi


def compute_macd(
    series: pd.Series,
    fast: int = MACD_FAST,
    slow: int = MACD_SLOW,
    signal: int = MACD_SIGNAL,
) -> tuple[pd.Series, pd.Series]:
    """MACD line and signal line."""
    ema_fast = compute_ema(series, fast)
    ema_slow = compute_ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = compute_ema(macd_line, signal)
    return macd_line, signal_line


def compute_bollinger_bands(
    series: pd.Series, window: int = 20, num_std: float = 2.0
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Bollinger Bands (upper, middle, lower)."""
    middle = compute_sma(series, window)
    std = series.rolling(window=window, min_periods=1).std()
    upper = middle + num_std * std
    lower = middle - num_std * std
    return upper, middle, lower


# ---------------------------------------------------------------------------
# Signal scoring helpers
# ---------------------------------------------------------------------------

def score_ma_crossover(close: pd.Series) -> float:
    """Score based on short-MA vs long-MA crossover.

    Returns 1.0 if short MA is above long MA (bullish), 0.0 otherwise.
    """
    short_ma = compute_sma(close, SHORT_MA_WINDOW)
    long_ma = compute_sma(close, LONG_MA_WINDOW)
    if short_ma.empty or long_ma.empty:
        return 0.5
    return 1.0 if short_ma.iloc[-1] > long_ma.iloc[-1] else 0.0


def score_rsi(close: pd.Series) -> float:
    """Score RSI: oversold (< 30) → bullish, overbought (> 70) → bearish."""
    rsi = compute_rsi(close)
    if rsi.empty:
        return 0.5
    last_rsi = rsi.iloc[-1]
    if last_rsi < 30:
        return 0.9
    if last_rsi < 50:
        return 0.6
    if last_rsi < 70:
        return 0.4
    return 0.1


def score_macd(close: pd.Series) -> float:
    """Score MACD: positive histogram → bullish."""
    macd_line, signal_line = compute_macd(close)
    if macd_line.empty or signal_line.empty:
        return 0.5
    histogram = macd_line.iloc[-1] - signal_line.iloc[-1]
    if histogram > 0:
        return 0.8
    return 0.2


def score_volume_trend(volume: pd.Series, window: int = 20) -> float:
    """Score based on recent volume vs average volume.

    Rising volume with positive price trend is bullish.
    """
    if volume.empty or len(volume) < window:
        return 0.5
    avg_volume = volume.rolling(window=window, min_periods=1).mean()
    ratio = volume.iloc[-1] / avg_volume.iloc[-1] if avg_volume.iloc[-1] > 0 else 1.0
    if ratio > 1.5:
        return 0.8
    if ratio > 1.0:
        return 0.6
    return 0.4


def score_bollinger(close: pd.Series) -> float:
    """Score Bollinger Band position.

    Price near lower band → bullish (oversold), near upper → bearish.
    """
    upper, middle, lower = compute_bollinger_bands(close)
    if upper.empty:
        return 0.5
    last_close = close.iloc[-1]
    band_width = upper.iloc[-1] - lower.iloc[-1]
    if band_width == 0:
        return 0.5
    position = (last_close - lower.iloc[-1]) / band_width
    # Invert: closer to lower band = more bullish (buying opportunity)
    return round(1.0 - position, 4)


# ---------------------------------------------------------------------------
# Main analysis entry point
# ---------------------------------------------------------------------------

def analyse_market(ticker: str, df: pd.DataFrame) -> MarketResult:
    """Perform full technical analysis on historical price data.

    Args:
        ticker: Stock ticker symbol.
        df: DataFrame with at least ``Close`` and ``Volume`` columns.

    Returns:
        A ``MarketResult`` with individual signal scores and an overall score.
    """
    if df.empty or "Close" not in df.columns:
        return MarketResult(ticker=ticker, summary="Insufficient data")

    close = df["Close"]
    volume = df["Volume"] if "Volume" in df.columns else pd.Series(dtype=float)

    signals: Dict[str, float] = {
        "ma_crossover": score_ma_crossover(close),
        "rsi": score_rsi(close),
        "macd": score_macd(close),
        "volume_trend": score_volume_trend(volume),
        "bollinger": score_bollinger(close),
    }

    last_rsi = compute_rsi(close).iloc[-1] if not close.empty else 50.0
    macd_line, signal_line = compute_macd(close)
    last_macd = macd_line.iloc[-1] if not macd_line.empty else 0.0

    indicators: Dict[str, float] = {
        "sma_short": round(compute_sma(close, SHORT_MA_WINDOW).iloc[-1], 2),
        "sma_long": round(compute_sma(close, LONG_MA_WINDOW).iloc[-1], 2),
        "rsi": round(last_rsi, 2),
        "macd": round(last_macd, 4),
        "last_close": round(close.iloc[-1], 2),
    }

    overall = sum(signals.values()) / len(signals)

    if overall >= 0.6:
        summary = "Technical indicators are bullish"
    elif overall >= 0.4:
        summary = "Technical indicators are neutral"
    else:
        summary = "Technical indicators are bearish"

    return MarketResult(
        ticker=ticker,
        indicators=indicators,
        signals=signals,
        overall_score=round(overall, 4),
        summary=summary,
    )
