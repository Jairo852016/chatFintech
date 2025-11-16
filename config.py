# config.py

# ETF principal
SPY_TICKER = "SPY"

# 7 Magníficas (puedes ajustar la lista)
MAGNIFICENT_7 = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA"]

# Lista completa de tickers a analizar
ALL_TICKERS = [SPY_TICKER] + MAGNIFICENT_7

# Parámetros por defecto para datos históricos
DEFAULT_PERIOD = "1y"        # 1 año
DEFAULT_INTERVAL = "1d"      # datos diarios

# Ventanas para indicadores
VOLATILITY_WINDOW = 20       # días
MOMENTUM_WINDOW = 10         # días
