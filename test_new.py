from core.news_fetcher import fetch_news_for_ticker

arts = fetch_news_for_ticker("SPY", limit=3)
print(arts)
