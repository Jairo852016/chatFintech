# core/news_fetcher.py
from __future__ import annotations

import os
import datetime as dt
from typing import List, Dict, Any

import requests

# Puedes poner la API key aquí o usar variable de entorno MARKET_AUX_API_KEY
API_KEY = os.getenv("MARKET_AUX_API_KEY") or "MOO3hXWObTTUZHhGt9yqcMvEBSrtRL3Wj000l25e"


BASE_URL = "https://api.marketaux.com/v1/news/all"


def fetch_news_for_ticker(ticker: str, limit: int = 5) -> List[Dict[str, Any]]:
    if not API_KEY or API_KEY == "TU_API_KEY_AQUI":
        print("[NEWS] ERROR: No API key configurada para MarketAux.")
        return []

    # ✅ Formato correcto: YYYY-MM-DD
    published_after = (dt.datetime.utcnow() - dt.timedelta(days=3)).strftime("%Y-%m-%d")

    params = {
        "symbols": ticker,
        "language": "en",
        "filter_entities": "true",
        "published_after": published_after,
        "limit": limit,
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    try:
        resp = requests.get(BASE_URL, params=params, headers=headers, timeout=10)
    except Exception as e:
        print(f"[NEWS] ERROR de conexión: {e}")
        return []

    print("[NEWS] status_code:", resp.status_code)

    if resp.status_code != 200:
        print("[NEWS] Response text:", resp.text[:400])
        return []

    data = resp.json()
    items = data.get("data", [])
    print(f"[NEWS] Encontradas {len(items)} noticias para {ticker}")

    articles: List[Dict[str, Any]] = []
    for item in items:
        articles.append({
            "title": item.get("title") or "Sin título",
            "publisher": item.get("source") or "Fuente desconocida",
            "link": item.get("url") or "",
            "published": item.get("published_at") or "",
        })

    return articles

def format_news_for_prompt(ticker: str, articles: List[Dict[str, Any]]) -> str:
    """
    Convierte la lista de noticias en texto para pasar al LLM.
    """
    if not articles:
        return f"No hay noticias recientes para {ticker}."

    lines = [f"Noticias recientes para {ticker}:\n"]

    for i, art in enumerate(articles, start=1):
        date_str = art.get("published") or "Fecha desconocida"
        publisher = art.get("publisher") or "Fuente desconocida"
        title = art.get("title") or f"Noticia {i}"
        link = art.get("link") or ""

        lines.append(
            f"{i}. [{date_str}] {publisher}: {title}\n"
            f"   Link: {link}"
        )

    return "\n".join(lines)
