"""Fundamental analysis module.

Evaluates a stock's fundamental health based on common financial metrics
obtained from stock info data (e.g. via yfinance). Each metric is scored
individually and then combined into an overall fundamental score in [0, 1].
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class FundamentalResult:
    """Container for fundamental analysis output."""

    ticker: str
    scores: Dict[str, float] = field(default_factory=dict)
    overall_score: float = 0.5
    summary: str = ""


def score_pe_ratio(pe: float | None) -> float:
    """Score P/E ratio.  Lower (but positive) is better.

    Returns a value in [0, 1].
    * pe <= 0 or None  → 0.3 (unable to evaluate)
    * pe <= 15         → 1.0 (deep value)
    * pe <= 25         → 0.7
    * pe <= 40         → 0.5
    * pe > 40          → 0.3
    """
    if pe is None or pe <= 0:
        return 0.3
    if pe <= 15:
        return 1.0
    if pe <= 25:
        return 0.7
    if pe <= 40:
        return 0.5
    return 0.3


def score_revenue_growth(growth: float | None) -> float:
    """Score revenue growth rate.

    * None       → 0.3
    * >= 30 %    → 1.0
    * >= 15 %    → 0.7
    * >= 0       → 0.5
    * < 0        → 0.2
    """
    if growth is None:
        return 0.3
    if growth >= 0.30:
        return 1.0
    if growth >= 0.15:
        return 0.7
    if growth >= 0:
        return 0.5
    return 0.2


def score_profit_margins(margin: float | None) -> float:
    """Score profit margins.

    * None       → 0.3
    * >= 25 %    → 1.0
    * >= 10 %    → 0.7
    * >= 0       → 0.5
    * < 0        → 0.2
    """
    if margin is None:
        return 0.3
    if margin >= 0.25:
        return 1.0
    if margin >= 0.10:
        return 0.7
    if margin >= 0:
        return 0.5
    return 0.2


def score_debt_to_equity(de: float | None) -> float:
    """Score debt-to-equity ratio.  Lower is better.

    * None       → 0.3
    * <= 30      → 1.0
    * <= 80      → 0.7
    * <= 150     → 0.5
    * > 150      → 0.3
    """
    if de is None:
        return 0.3
    if de <= 30:
        return 1.0
    if de <= 80:
        return 0.7
    if de <= 150:
        return 0.5
    return 0.3


def score_roe(roe: float | None) -> float:
    """Score return on equity.

    * None       → 0.3
    * >= 25 %    → 1.0
    * >= 15 %    → 0.7
    * >= 5 %     → 0.5
    * < 5 %      → 0.3
    """
    if roe is None:
        return 0.3
    if roe >= 0.25:
        return 1.0
    if roe >= 0.15:
        return 0.7
    if roe >= 0.05:
        return 0.5
    return 0.3


def analyse_fundamentals(ticker: str, info: dict) -> FundamentalResult:
    """Perform fundamental analysis on a stock.

    Args:
        ticker: Stock ticker symbol.
        info: Dictionary of stock information (typically from ``yfinance``).

    Returns:
        A ``FundamentalResult`` with individual and overall scores.
    """
    scores: Dict[str, float] = {
        "pe_ratio": score_pe_ratio(info.get("trailingPE")),
        "revenue_growth": score_revenue_growth(info.get("revenueGrowth")),
        "profit_margins": score_profit_margins(info.get("profitMargins")),
        "debt_to_equity": score_debt_to_equity(info.get("debtToEquity")),
        "roe": score_roe(info.get("returnOnEquity")),
    }

    overall = sum(scores.values()) / len(scores) if scores else 0.5

    if overall >= 0.7:
        summary = "Strong fundamentals – bullish"
    elif overall >= 0.5:
        summary = "Moderate fundamentals – neutral"
    else:
        summary = "Weak fundamentals – bearish"

    return FundamentalResult(
        ticker=ticker,
        scores=scores,
        overall_score=round(overall, 4),
        summary=summary,
    )
