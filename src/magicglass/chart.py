"""Chart generation for stock data."""

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def plot_stock_trend(hist, symbol, output_path=None):
    """Generate a stock trend chart and save to file.

    Args:
        hist: pandas DataFrame from yfinance history.
        symbol: Stock ticker symbol for the title.
        output_path: File path to save the chart. Defaults to '{symbol}_trend.png'.

    Returns:
        The path to the saved chart image.
    """
    if output_path is None:
        output_path = f"{symbol}_trend.png"

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), height_ratios=[3, 1],
                                    sharex=True)
    fig.suptitle(f"{symbol} Stock Trend", fontsize=16, fontweight="bold")

    # Price chart
    ax1.plot(hist.index, hist["Close"], label="Close", color="#1f77b4", linewidth=1.5)

    if len(hist) >= 20:
        sma20 = hist["Close"].rolling(window=20).mean()
        ax1.plot(hist.index, sma20, label="SMA 20", color="#ff7f0e",
                 linewidth=1, linestyle="--")

    if len(hist) >= 50:
        sma50 = hist["Close"].rolling(window=50).mean()
        ax1.plot(hist.index, sma50, label="SMA 50", color="#2ca02c",
                 linewidth=1, linestyle="--")

    ax1.set_ylabel("Price (USD)")
    ax1.legend(loc="upper left")
    ax1.grid(True, alpha=0.3)

    # Volume chart
    colors = ["#2ca02c" if hist["Close"].iloc[i] >= hist["Open"].iloc[i]
              else "#d62728" for i in range(len(hist))]
    ax2.bar(hist.index, hist["Volume"], color=colors, alpha=0.7, width=1.5)
    ax2.set_ylabel("Volume")
    ax2.grid(True, alpha=0.3)

    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return output_path
