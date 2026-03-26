"""Prediction module.

Combines sentiment, fundamental, and market analysis scores into a
final probability estimate for whether a stock's price will go up or down.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from magicglass.config import WEIGHTS


@dataclass
class PredictionResult:
    """Final prediction for a single stock."""

    ticker: str
    company: str
    sentiment_score: float
    fundamental_score: float
    market_score: float
    probability_up: float
    probability_down: float
    signal: str  # "BUY", "SELL", or "HOLD"
    details: Dict[str, str] = field(default_factory=dict)


def combine_scores(
    sentiment_score: float,
    fundamental_score: float,
    market_score: float,
    weights: Dict[str, float] | None = None,
) -> float:
    """Compute the weighted probability of a price increase.

    Each input score should be in [0, 1].  The returned value is also
    in [0, 1] and represents the estimated probability of an upward move.

    Args:
        sentiment_score: Score from sentiment analysis.
        fundamental_score: Score from fundamental analysis.
        market_score: Score from market / technical analysis.
        weights: Optional custom weights dict with keys
                 ``sentiment``, ``fundamental``, ``market``.

    Returns:
        Weighted combined probability in [0, 1].
    """
    if weights is None:
        weights = WEIGHTS

    total_weight = sum(weights.values())
    if total_weight == 0:
        return 0.5

    weighted_sum = (
        sentiment_score * weights.get("sentiment", 0)
        + fundamental_score * weights.get("fundamental", 0)
        + market_score * weights.get("market", 0)
    )

    return round(min(max(weighted_sum / total_weight, 0.0), 1.0), 4)


def make_prediction(
    ticker: str,
    company: str,
    sentiment_score: float,
    fundamental_score: float,
    market_score: float,
    sentiment_summary: str = "",
    fundamental_summary: str = "",
    market_summary: str = "",
) -> PredictionResult:
    """Generate a final prediction for a stock.

    Args:
        ticker: Stock ticker symbol.
        company: Company name.
        sentiment_score: Normalised sentiment score [0, 1].
        fundamental_score: Normalised fundamental score [0, 1].
        market_score: Normalised market score [0, 1].
        sentiment_summary: Human-readable sentiment summary.
        fundamental_summary: Human-readable fundamental summary.
        market_summary: Human-readable market summary.

    Returns:
        A ``PredictionResult`` with the combined prediction.
    """
    prob_up = combine_scores(sentiment_score, fundamental_score, market_score)
    prob_down = round(1.0 - prob_up, 4)

    if prob_up >= 0.6:
        signal = "BUY"
    elif prob_up <= 0.4:
        signal = "SELL"
    else:
        signal = "HOLD"

    details = {
        "sentiment": sentiment_summary,
        "fundamental": fundamental_summary,
        "market": market_summary,
    }

    return PredictionResult(
        ticker=ticker,
        company=company,
        sentiment_score=round(sentiment_score, 4),
        fundamental_score=round(fundamental_score, 4),
        market_score=round(market_score, 4),
        probability_up=prob_up,
        probability_down=prob_down,
        signal=signal,
        details=details,
    )
