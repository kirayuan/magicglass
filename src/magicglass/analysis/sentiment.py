"""Sentiment analysis module.

Performs text-based sentiment analysis on stock-related news headlines.
Uses TextBlob for polarity scoring and converts results to a bullish/bearish
signal in the range [0, 1].
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from textblob import TextBlob


@dataclass
class SentimentResult:
    """Container for sentiment analysis output."""

    ticker: str
    avg_polarity: float  # -1.0 (bearish) to 1.0 (bullish)
    score: float  # normalised to 0..1 for the predictor
    headline_count: int
    summary: str


def analyse_headlines(headlines: List[str]) -> float:
    """Return the average polarity of a list of headlines.

    Polarity is in [-1.0, 1.0] where negative is bearish and positive is bullish.
    Returns 0.0 when no headlines are provided.
    """
    if not headlines:
        return 0.0
    polarities = [TextBlob(h).sentiment.polarity for h in headlines]
    return sum(polarities) / len(polarities)


def polarity_to_score(polarity: float) -> float:
    """Map polarity from [-1, 1] to a probability-like score in [0, 1].

    A polarity of -1 maps to 0 (strong bearish), 0 maps to 0.5 (neutral),
    and 1 maps to 1 (strong bullish).
    """
    return (polarity + 1.0) / 2.0


def analyse_stock_sentiment(ticker: str, headlines: List[str]) -> SentimentResult:
    """Run full sentiment analysis for a single stock.

    Args:
        ticker: Stock ticker symbol.
        headlines: List of recent news headline strings.

    Returns:
        A ``SentimentResult`` with the aggregated sentiment metrics.
    """
    avg_polarity = analyse_headlines(headlines)
    score = polarity_to_score(avg_polarity)

    if avg_polarity > 0.1:
        summary = "Positive sentiment – bullish bias"
    elif avg_polarity < -0.1:
        summary = "Negative sentiment – bearish bias"
    else:
        summary = "Neutral sentiment"

    return SentimentResult(
        ticker=ticker,
        avg_polarity=round(avg_polarity, 4),
        score=round(score, 4),
        headline_count=len(headlines),
        summary=summary,
    )
