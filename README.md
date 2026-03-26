# MagicGlass

Quantitative trading analysis tool for AI-related stocks. Combines **sentiment analysis**, **fundamental analysis**, and **market/technical analysis** to predict stock price movement probabilities.

## Features

- **AI Stock Universe** – Pre-configured list of 15 major AI stocks (NVDA, MSFT, GOOGL, META, AMD, etc.)
- **Sentiment Analysis** – Analyses news headlines using NLP polarity scoring to detect bullish/bearish bias
- **Fundamental Analysis** – Evaluates P/E ratio, revenue growth, profit margins, debt-to-equity, and ROE
- **Market / Technical Analysis** – Computes SMA crossover, RSI, MACD, Bollinger Bands, and volume trends
- **Prediction Engine** – Combines all three signals with configurable weights to produce an overall up/down probability and BUY/HOLD/SELL signal

## Project Structure

```
magicglass/
├── config/
│   └── stocks.py                # Stock tickers and analysis parameters
├── src/magicglass/
│   ├── data/
│   │   └── stock_data.py        # Stock data fetching (yfinance)
│   ├── analysis/
│   │   ├── sentiment.py         # Sentiment analysis (TextBlob)
│   │   ├── fundamental.py       # Fundamental analysis
│   │   └── market.py            # Technical indicators & signals
│   ├── prediction/
│   │   └── predictor.py         # Weighted prediction combiner
│   └── main.py                  # Orchestrator & CLI entry point
├── tests/                       # Unit tests (pytest)
├── requirements.txt
└── setup.py
```

## Quick Start

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the analysis

```bash
python src/magicglass/main.py
```

### Run tests

```bash
python -m pytest tests/ -v
```

## Configuration

Edit `config/stocks.py` to:

- Add or remove stock tickers in `AI_STOCKS`
- Adjust technical indicator parameters (MA windows, RSI period, etc.)
- Tune prediction weights for sentiment, fundamental, and market signals

## How It Works

1. **Data Fetching** – Downloads 180 days of historical OHLCV data for each stock via `yfinance`
2. **Sentiment Analysis** – Scores news headlines on a polarity scale (-1 bearish … +1 bullish) then normalises to [0, 1]
3. **Fundamental Analysis** – Scores five key financial metrics individually and averages them
4. **Market Analysis** – Computes five technical signals (MA crossover, RSI, MACD, Bollinger, volume) and averages them
5. **Prediction** – Weighted combination of the three analysis scores produces a probability of price increase and a BUY / HOLD / SELL recommendation
