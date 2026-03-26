"""Tests for sentiment analysis module."""

from magicglass.analysis.sentiment import (
    SentimentResult,
    analyse_headlines,
    analyse_stock_sentiment,
    polarity_to_score,
)


class TestAnalyseHeadlines:
    def test_empty_headlines_returns_zero(self):
        assert analyse_headlines([]) == 0.0

    def test_positive_headlines(self):
        headlines = [
            "Company reports record profits and strong growth",
            "Stock surges on excellent earnings beat",
            "Analysts raise price target significantly",
        ]
        polarity = analyse_headlines(headlines)
        assert polarity > 0.0

    def test_negative_headlines(self):
        headlines = [
            "Company reports disappointing losses",
            "Stock crashes on terrible earnings miss",
            "Analysts downgrade stock amid concerns",
        ]
        polarity = analyse_headlines(headlines)
        assert polarity < 0.0

    def test_mixed_headlines(self):
        headlines = [
            "Great earnings report surprises analysts",
            "Terrible outlook for next quarter",
        ]
        polarity = analyse_headlines(headlines)
        # Just verify it returns a number in range
        assert -1.0 <= polarity <= 1.0


class TestPolarityToScore:
    def test_max_bullish(self):
        assert polarity_to_score(1.0) == 1.0

    def test_max_bearish(self):
        assert polarity_to_score(-1.0) == 0.0

    def test_neutral(self):
        assert polarity_to_score(0.0) == 0.5

    def test_positive_polarity(self):
        score = polarity_to_score(0.5)
        assert 0.5 < score <= 1.0

    def test_negative_polarity(self):
        score = polarity_to_score(-0.5)
        assert 0.0 <= score < 0.5


class TestAnalyseStockSentiment:
    def test_returns_sentiment_result(self):
        result = analyse_stock_sentiment("TEST", ["Great news for the stock market"])
        assert isinstance(result, SentimentResult)
        assert result.ticker == "TEST"
        assert result.headline_count == 1
        assert 0.0 <= result.score <= 1.0

    def test_positive_sentiment_summary(self):
        headlines = [
            "Amazing breakthrough leads to huge profits",
            "Stock soars on wonderful earnings",
        ]
        result = analyse_stock_sentiment("TEST", headlines)
        assert "bullish" in result.summary.lower() or "neutral" in result.summary.lower()

    def test_empty_headlines(self):
        result = analyse_stock_sentiment("TEST", [])
        assert result.headline_count == 0
        assert result.score == 0.5  # neutral
        assert result.avg_polarity == 0.0
