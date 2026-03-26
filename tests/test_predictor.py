"""Tests for prediction module."""

from magicglass.prediction.predictor import (
    PredictionResult,
    combine_scores,
    make_prediction,
)


class TestCombineScores:
    def test_all_bullish(self):
        score = combine_scores(1.0, 1.0, 1.0)
        assert score == 1.0

    def test_all_bearish(self):
        score = combine_scores(0.0, 0.0, 0.0)
        assert score == 0.0

    def test_neutral(self):
        score = combine_scores(0.5, 0.5, 0.5)
        assert score == 0.5

    def test_custom_weights(self):
        weights = {"sentiment": 0.5, "fundamental": 0.3, "market": 0.2}
        score = combine_scores(1.0, 0.5, 0.0, weights=weights)
        expected = (1.0 * 0.5 + 0.5 * 0.3 + 0.0 * 0.2) / 1.0
        assert abs(score - expected) < 0.001

    def test_zero_weights(self):
        weights = {"sentiment": 0.0, "fundamental": 0.0, "market": 0.0}
        score = combine_scores(1.0, 1.0, 1.0, weights=weights)
        assert score == 0.5  # fallback neutral

    def test_result_clamped(self):
        # Verify scores stay within [0, 1]
        score = combine_scores(1.0, 1.0, 1.0)
        assert 0.0 <= score <= 1.0
        score = combine_scores(0.0, 0.0, 0.0)
        assert 0.0 <= score <= 1.0


class TestMakePrediction:
    def test_buy_signal(self):
        pred = make_prediction(
            ticker="TEST",
            company="Test Corp",
            sentiment_score=0.8,
            fundamental_score=0.9,
            market_score=0.7,
        )
        assert isinstance(pred, PredictionResult)
        assert pred.signal == "BUY"
        assert pred.probability_up > 0.6

    def test_sell_signal(self):
        pred = make_prediction(
            ticker="TEST",
            company="Test Corp",
            sentiment_score=0.1,
            fundamental_score=0.2,
            market_score=0.1,
        )
        assert pred.signal == "SELL"
        assert pred.probability_up < 0.4

    def test_hold_signal(self):
        pred = make_prediction(
            ticker="TEST",
            company="Test Corp",
            sentiment_score=0.5,
            fundamental_score=0.5,
            market_score=0.5,
        )
        assert pred.signal == "HOLD"
        assert abs(pred.probability_up - 0.5) < 0.01

    def test_probability_sum_to_one(self):
        pred = make_prediction(
            ticker="TEST",
            company="Test Corp",
            sentiment_score=0.7,
            fundamental_score=0.3,
            market_score=0.6,
        )
        assert abs(pred.probability_up + pred.probability_down - 1.0) < 0.001

    def test_details_populated(self):
        pred = make_prediction(
            ticker="TEST",
            company="Test Corp",
            sentiment_score=0.5,
            fundamental_score=0.5,
            market_score=0.5,
            sentiment_summary="Neutral",
            fundamental_summary="Moderate",
            market_summary="Flat",
        )
        assert pred.details["sentiment"] == "Neutral"
        assert pred.details["fundamental"] == "Moderate"
        assert pred.details["market"] == "Flat"

    def test_ticker_and_company(self):
        pred = make_prediction(
            ticker="NVDA",
            company="NVIDIA Corporation",
            sentiment_score=0.5,
            fundamental_score=0.5,
            market_score=0.5,
        )
        assert pred.ticker == "NVDA"
        assert pred.company == "NVIDIA Corporation"
