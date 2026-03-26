"""Stock data fetching and trend analysis."""

import yfinance as yf
import pandas as pd
import numpy as np


def fetch_stock_data(symbol, period="1y"):
    """Fetch historical stock data for the given symbol.

    Args:
        symbol: Stock ticker symbol (e.g., 'BABA').
        period: Data period to download. Valid values: '1d', '5d', '1mo',
                '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'.

    Returns:
        pandas DataFrame with stock history, or None if download fails.
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        if hist.empty:
            return None
        return hist
    except Exception as e:
        print(f"Warning: Could not fetch live data for {symbol}: {e}")
        return None


def get_stock_info(symbol):
    """Get basic information about a stock.

    Args:
        symbol: Stock ticker symbol.

    Returns:
        dict with stock info, or empty dict on failure.
    """
    try:
        ticker = yf.Ticker(symbol)
        return ticker.info
    except Exception:
        return {}


def generate_sample_data(symbol="BABA", num_days=252):
    """Generate realistic sample stock data for demonstration.

    Uses a random walk model seeded by the symbol name for reproducibility.
    The generated data mimics BABA's approximate price range.

    Args:
        symbol: Stock ticker symbol (used for seed).
        num_days: Number of trading days to generate.

    Returns:
        pandas DataFrame matching yfinance history format.
    """
    seed = sum(ord(c) for c in symbol)
    rng = np.random.RandomState(seed)

    dates = pd.bdate_range(end=pd.Timestamp.now(), periods=num_days)

    # Start around a realistic price for the symbol
    start_price = 80.0 if symbol == "BABA" else 100.0

    # Random walk with slight upward drift
    daily_returns = rng.normal(loc=0.0005, scale=0.025, size=num_days)
    prices = start_price * np.cumprod(1 + daily_returns)

    # Generate OHLCV data
    high = prices * (1 + rng.uniform(0.005, 0.03, size=num_days))
    low = prices * (1 - rng.uniform(0.005, 0.03, size=num_days))
    open_prices = low + (high - low) * rng.uniform(0.2, 0.8, size=num_days)
    volume = rng.randint(5_000_000, 30_000_000, size=num_days)

    return pd.DataFrame(
        {
            "Open": open_prices,
            "High": high,
            "Low": low,
            "Close": prices,
            "Volume": volume,
        },
        index=dates,
    )


def compute_trend_summary(hist):
    """Compute a trend summary from historical data.

    Args:
        hist: pandas DataFrame from yfinance history.

    Returns:
        dict with trend summary statistics.
    """
    if hist is None or hist.empty:
        return {}

    latest = hist.iloc[-1]
    earliest = hist.iloc[0]

    price_change = latest["Close"] - earliest["Close"]
    price_change_pct = (price_change / earliest["Close"]) * 100

    high_52w = hist["High"].max()
    low_52w = hist["Low"].min()
    avg_volume = hist["Volume"].mean()

    # Simple moving averages
    sma_20 = hist["Close"].rolling(window=20).mean().iloc[-1] if len(hist) >= 20 else None
    sma_50 = hist["Close"].rolling(window=50).mean().iloc[-1] if len(hist) >= 50 else None

    return {
        "current_price": latest["Close"],
        "period_start_price": earliest["Close"],
        "price_change": price_change,
        "price_change_pct": price_change_pct,
        "high_52w": high_52w,
        "low_52w": low_52w,
        "avg_volume": avg_volume,
        "sma_20": sma_20,
        "sma_50": sma_50,
    }


def format_trend_report(symbol, summary):
    """Format a human-readable trend report.

    Args:
        symbol: Stock ticker symbol.
        summary: dict from compute_trend_summary.

    Returns:
        Formatted string report.
    """
    if not summary:
        return f"No data available for {symbol}."

    lines = [
        f"{'='*50}",
        f"  Stock Trend Report: {symbol}",
        f"{'='*50}",
        f"  Current Price:      ${summary['current_price']:.2f}",
        f"  Period Start Price: ${summary['period_start_price']:.2f}",
        f"  Price Change:       ${summary['price_change']:+.2f} ({summary['price_change_pct']:+.2f}%)",
        f"  52-Week High:       ${summary['high_52w']:.2f}",
        f"  52-Week Low:        ${summary['low_52w']:.2f}",
        f"  Avg Daily Volume:   {summary['avg_volume']:,.0f}",
    ]

    if summary.get("sma_20") is not None:
        lines.append(f"  SMA (20-day):       ${summary['sma_20']:.2f}")
    if summary.get("sma_50") is not None:
        lines.append(f"  SMA (50-day):       ${summary['sma_50']:.2f}")

    # Trend direction
    if summary["price_change_pct"] > 5:
        trend = "📈 UPTREND"
    elif summary["price_change_pct"] < -5:
        trend = "📉 DOWNTREND"
    else:
        trend = "➡️  SIDEWAYS"

    lines.append(f"  Trend:              {trend}")
    lines.append(f"{'='*50}")

    return "\n".join(lines)
