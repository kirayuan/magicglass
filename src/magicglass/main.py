"""MagicGlass – main entry point.

Orchestrates data fetching, sentiment / fundamental / market analysis,
and outputs a prediction report for each configured AI stock.
"""

from __future__ import annotations

import sys

sys.path.insert(0, ".")

from config.stocks import AI_STOCKS
from src.magicglass.analysis.fundamental import analyse_fundamentals
from src.magicglass.analysis.market import analyse_market
from src.magicglass.analysis.sentiment import analyse_stock_sentiment
from src.magicglass.data.stock_data import fetch_all_stocks, fetch_stock_info
from src.magicglass.prediction.predictor import PredictionResult, make_prediction


# ---------------------------------------------------------------------------
# Placeholder headline provider – replace with a real news API integration
# ---------------------------------------------------------------------------

_SAMPLE_HEADLINES: dict[str, list[str]] = {
    "NVDA": [
        "NVIDIA reports record data-center revenue driven by AI demand",
        "NVIDIA stock surges on strong earnings beat",
        "Analysts raise NVIDIA price target after blowout quarter",
    ],
    "MSFT": [
        "Microsoft Azure AI services see rapid adoption",
        "Microsoft invests billions in OpenAI partnership",
        "Microsoft stock holds steady amid tech sell-off",
    ],
    "GOOGL": [
        "Google launches Gemini 2.0 AI model",
        "Alphabet reports strong ad revenue growth",
        "Concerns over AI regulation weigh on Google stock",
    ],
    "META": [
        "Meta's Llama models gain enterprise traction",
        "Meta Reality Labs losses widen but AI ad revenue grows",
        "Meta stock rises on better-than-expected guidance",
    ],
    "AMZN": [
        "Amazon AWS launches new AI training chips",
        "Amazon reports strong cloud growth",
        "Amazon faces antitrust scrutiny but AI business booms",
    ],
}


def _get_headlines(ticker: str) -> list[str]:
    """Return sample headlines for a ticker (stub for real news API)."""
    return _SAMPLE_HEADLINES.get(ticker, [
        f"{ticker} shows steady performance in AI sector",
        f"Analysts maintain neutral outlook on {ticker}",
    ])


# ---------------------------------------------------------------------------
# Report formatting
# ---------------------------------------------------------------------------

def format_prediction(pred: PredictionResult) -> str:
    """Format a single prediction into a human-readable block."""
    lines = [
        f"{'=' * 60}",
        f"  {pred.ticker} – {pred.company}",
        f"{'=' * 60}",
        f"  Sentiment score  : {pred.sentiment_score:.2%}",
        f"  Fundamental score: {pred.fundamental_score:.2%}",
        f"  Market score     : {pred.market_score:.2%}",
        f"  -----------------------------------------------",
        f"  Probability UP   : {pred.probability_up:.2%}",
        f"  Probability DOWN : {pred.probability_down:.2%}",
        f"  Signal           : {pred.signal}",
        f"  -----------------------------------------------",
    ]
    for key, val in pred.details.items():
        if val:
            lines.append(f"  [{key}] {val}")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_analysis() -> list[PredictionResult]:
    """Run the full analysis pipeline and return predictions."""
    print("MagicGlass – AI Stock Quantitative Analysis")
    print("=" * 60)
    print(f"Analysing {len(AI_STOCKS)} AI-related stocks …\n")

    # 1. Fetch historical price data
    print("[1/4] Fetching historical price data …")
    stock_data = fetch_all_stocks()
    print(f"      Retrieved data for {len(stock_data)} stocks.\n")

    predictions: list[PredictionResult] = []

    for ticker, company in AI_STOCKS.items():
        # 2. Sentiment analysis
        headlines = _get_headlines(ticker)
        sentiment_result = analyse_stock_sentiment(ticker, headlines)

        # 3. Fundamental analysis
        info = fetch_stock_info(ticker)
        fundamental_result = analyse_fundamentals(ticker, info)

        # 4. Market / technical analysis
        df = stock_data.get(ticker)
        if df is not None and not df.empty:
            market_result = analyse_market(ticker, df)
        else:
            from src.magicglass.analysis.market import MarketResult
            market_result = MarketResult(ticker=ticker, summary="No price data available")

        # 5. Prediction
        pred = make_prediction(
            ticker=ticker,
            company=company,
            sentiment_score=sentiment_result.score,
            fundamental_score=fundamental_result.overall_score,
            market_score=market_result.overall_score,
            sentiment_summary=sentiment_result.summary,
            fundamental_summary=fundamental_result.summary,
            market_summary=market_result.summary,
        )
        predictions.append(pred)

    return predictions


def main() -> None:
    """Entry point."""
    predictions = run_analysis()

    print("\n" + "=" * 60)
    print("  PREDICTION REPORT")
    print("=" * 60 + "\n")

    for pred in predictions:
        print(format_prediction(pred))

    # Summary table
    print("\n" + "=" * 60)
    print("  SUMMARY TABLE")
    print("=" * 60)
    print(f"  {'Ticker':<8} {'Company':<28} {'P(Up)':>8} {'Signal':>8}")
    print(f"  {'-' * 56}")
    for pred in predictions:
        print(
            f"  {pred.ticker:<8} {pred.company:<28} {pred.probability_up:>7.2%} {pred.signal:>8}"
        )
    print()


if __name__ == "__main__":
    main()
