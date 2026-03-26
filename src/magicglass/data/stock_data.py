"""Stock data fetching module.

Provides functionality to download historical stock data and basic info
for the configured AI stock tickers using the yfinance library.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

import pandas as pd
import yfinance as yf

from magicglass.config import AI_STOCKS, LOOKBACK_DAYS

logger = logging.getLogger(__name__)


def fetch_stock_history(
    ticker: str, days: int = LOOKBACK_DAYS
) -> pd.DataFrame:
    """Fetch historical OHLCV data for a single stock ticker.

    Args:
        ticker: Stock ticker symbol (e.g. "NVDA").
        days: Number of calendar days of history to retrieve.

    Returns:
        DataFrame with columns [Open, High, Low, Close, Volume] indexed by date.
        Returns an empty DataFrame if the download fails.
    """
    end = datetime.now()
    start = end - timedelta(days=days)
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"))
        if df.empty:
            return pd.DataFrame()
        return df[["Open", "High", "Low", "Close", "Volume"]]
    except Exception:
        logger.warning("Failed to fetch history for %s", ticker)
        return pd.DataFrame()


def fetch_all_stocks(
    tickers: Optional[Dict[str, str]] = None, days: int = LOOKBACK_DAYS
) -> Dict[str, pd.DataFrame]:
    """Fetch historical data for all configured AI stocks.

    Args:
        tickers: Mapping of ticker symbol to company name.
                 Defaults to ``AI_STOCKS`` from config.
        days: Number of calendar days of history.

    Returns:
        Dictionary mapping ticker symbols to their history DataFrames.
    """
    if tickers is None:
        tickers = AI_STOCKS

    results: Dict[str, pd.DataFrame] = {}
    for ticker in tickers:
        df = fetch_stock_history(ticker, days)
        if not df.empty:
            results[ticker] = df
    return results


def fetch_stock_info(ticker: str) -> dict:
    """Fetch fundamental information for a stock.

    Returns a dict with keys such as ``trailingPE``, ``forwardPE``,
    ``marketCap``, ``revenueGrowth``, ``profitMargins``, etc.
    Returns an empty dict on failure.
    """
    try:
        stock = yf.Ticker(ticker)
        return stock.info
    except Exception:
        logger.warning("Failed to fetch info for %s", ticker)
        return {}
