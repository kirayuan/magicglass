"""Configuration for AI stock tickers and analysis parameters."""

# Major AI-related stocks
AI_STOCKS = {
    "NVDA": "NVIDIA Corporation",
    "MSFT": "Microsoft Corporation",
    "GOOGL": "Alphabet Inc.",
    "META": "Meta Platforms Inc.",
    "AMZN": "Amazon.com Inc.",
    "TSM": "Taiwan Semiconductor",
    "AVGO": "Broadcom Inc.",
    "AMD": "Advanced Micro Devices",
    "ORCL": "Oracle Corporation",
    "CRM": "Salesforce Inc.",
    "PLTR": "Palantir Technologies",
    "AI": "C3.ai Inc.",
    "PATH": "UiPath Inc.",
    "SNOW": "Snowflake Inc.",
    "MDB": "MongoDB Inc.",
}

# Analysis parameters
LOOKBACK_DAYS = 180
SHORT_MA_WINDOW = 20
LONG_MA_WINDOW = 50
RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# Prediction weights for combining signals
WEIGHTS = {
    "sentiment": 0.25,
    "fundamental": 0.35,
    "market": 0.40,
}
