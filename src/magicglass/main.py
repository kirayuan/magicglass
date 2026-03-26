"""Main entry point for MagicGlass stock trend analysis."""

import argparse
import sys

from magicglass.stock import (
    fetch_stock_data,
    generate_sample_data,
    compute_trend_summary,
    format_trend_report,
)
from magicglass.chart import plot_stock_trend


def main(argv=None):
    """Run the stock trend analysis.

    Args:
        argv: Command-line arguments. Defaults to sys.argv[1:].

    Returns:
        0 on success, 1 on failure.
    """
    parser = argparse.ArgumentParser(
        description="MagicGlass - Stock trend analysis tool"
    )
    parser.add_argument(
        "symbol",
        nargs="?",
        default="BABA",
        help="Stock ticker symbol (default: BABA)",
    )
    parser.add_argument(
        "--period",
        default="1y",
        choices=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
        help="Data period (default: 1y)",
    )
    parser.add_argument(
        "--no-chart",
        action="store_true",
        help="Skip chart generation",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output path for the chart image",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Use generated sample data (no network required)",
    )

    args = parser.parse_args(argv)
    symbol = args.symbol.upper()

    if args.demo:
        print(f"Generating sample data for {symbol} (demo mode)...")
        hist = generate_sample_data(symbol)
    else:
        print(f"Fetching stock data for {symbol} (period: {args.period})...")
        hist = fetch_stock_data(symbol, period=args.period)
        if hist is None:
            print(f"Could not fetch live data for {symbol}. Falling back to demo mode...")
            hist = generate_sample_data(symbol)

    summary = compute_trend_summary(hist)
    report = format_trend_report(symbol, summary)
    print(report)

    if not args.no_chart:
        output_path = args.output or f"{symbol}_trend.png"
        chart_path = plot_stock_trend(hist, symbol, output_path=output_path)
        print(f"\nChart saved to: {chart_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
