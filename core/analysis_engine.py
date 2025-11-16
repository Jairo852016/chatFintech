# core/analysis_engine.py
from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Dict, Any

from core.financial_data import (
    compute_volatility,
    compute_momentum,
    intraday_high_low,
    seasonality_by_month,
)


# -------------------------------------------------------------
# 1) NORMALIZACIÓN DE MÉTRICAS
# -------------------------------------------------------------
def score_normalize(value: float, low: float, high: float) -> float:
    """
    Normaliza un valor en el rango [low, high] y lo convierte en score 0–1.
    Funciona como un indicador de intensidad.
    """
    if value is None or np.isnan(value):
        return 0.5
    return max(0, min(1, (value - low) / (high - low)))


# -------------------------------------------------------------
# 2) DETECCIÓN DE ANOMALÍAS EN RENDIMIENTOS
# -------------------------------------------------------------
def detect_return_anomaly(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Detecta si el rendimiento del último día es inusualmente alto o bajo.
    Usa desviaciones estándar del último mes.
    """
    df = df.copy()
    df["ret"] = df["Close"].pct_change()
    recent = df["ret"].tail(20).dropna()

    if len(recent) < 5:
        return {"anomaly": False, "sigma": 0}

    mean = recent.mean()
    std = recent.std()
    last_ret = recent.iloc[-1]
    z = (last_ret - mean) / std if std > 0 else 0

    return {
        "anomaly": abs(z) >= 2,
        "sigma": float(z),
        "last_ret": float(last_ret)
    }


# -------------------------------------------------------------
# 3) CLASIFICACIÓN DE MOMENTUM
# -------------------------------------------------------------
def classify_momentum(momentum: float) -> str:
    if momentum > 0.05:
        return "📈 Momentum fuertemente alcista"
    elif momentum > 0.01:
        return "↗️ Momentum moderadamente alcista"
    elif momentum > -0.01:
        return "➡️ Momentum neutral"
    elif momentum > -0.05:
        return "↘️ Momentum moderadamente bajista"
    else:
        return "📉 Momentum fuertemente bajista"


# -------------------------------------------------------------
# 4) GENERAR CONTEXTO MACRO PARA EL DÍA
# -------------------------------------------------------------
def generate_macro_context(ticker: str, df: pd.DataFrame) -> Dict[str, Any]:
    """
    Genera un análisis macro simple:
    - Volatilidad actual vs normal
    - Momentum
    - Detección de anomalías
    - Rango del último día
    - Estacionalidad del mes
    """
    # Métricas básicas
    volatility = compute_volatility(df)
    momentum = compute_momentum(df)
    day_info = intraday_high_low(df)
    anomaly_info = detect_return_anomaly(df)

    # Estacionalidad mensual
    current_month = df["date"].iloc[-1].month
    seasonality = seasonality_by_month(df)
    season_row = seasonality[seasonality["month"] == current_month]

    if not season_row.empty:
        avg_month_return = float(season_row["avg_return"].iloc[0])
    else:
        avg_month_return = None

    # Clasificación momentum
    momentum_summary = classify_momentum(momentum)

    # Construcción de texto
    macro_text = f"""
Análisis macro del día para {ticker}:

• Volatilidad anualizada (20 días): {volatility:.2%}
• {momentum_summary} (momentum {momentum:.2%})
• Rango del último día: High {day_info['high']:.2f}, Low {day_info['low']:.2f}

"""

    # Anomalía
    if anomaly_info["anomaly"]:
        macro_text += f"⚠️ Anomalía detectada: movimiento inusualmente fuerte ({anomaly_info['sigma']:.2f} σ).\n"
    else:
        macro_text += "No hay anomalías significativas en el rendimiento reciente.\n"

    # Estacionalidad
    if avg_month_return is not None:
        macro_text += f"• Estacionalidad del mes: retorno promedio {avg_month_return:.2%}\n"

    # Score general (esto lo puede usar el LLM)
    score_vol = score_normalize(volatility, 0.10, 0.40)
    score_mom = score_normalize(momentum, -0.05, 0.05)

    overall_score = round((score_vol * 0.4 + score_mom * 0.6), 3)

    return {
        "ticker": ticker,
        "volatility": volatility,
        "momentum": momentum,
        "momentum_summary": momentum_summary,
        "day_info": day_info,
        "anomaly_info": anomaly_info,
        "avg_month_return": avg_month_return,
        "macro_text": macro_text,
        "overall_score": overall_score,
    }


# -------------------------------------------------------------
# 5) GENERAR TEXTO LISTO PARA EL CHATBOT
# -------------------------------------------------------------
def format_context_for_llm(context: Dict[str, Any]) -> str:
    """
    Convierte el contexto macro en un texto bonito para el prompt del LLM.
    """
    txt = (
        f"Ticker: {context['ticker']}\n"
        f"Volatilidad 20d: {context['volatility']:.2%}\n"
        f"Momentum 10d: {context['momentum']:.2%}\n"
        f"{context['momentum_summary']}\n"
        f"Último rango: High {context['day_info']['high']:.2f}, "
        f"Low {context['day_info']['low']:.2f}\n"
    )

    if context["anomaly_info"]["anomaly"]:
        txt += (
            f"Anomalía detectada en rendimientos: Z-score {context['anomaly_info']['sigma']:.2f}\n"
        )
    if context["avg_month_return"] is not None:
        txt += f"Estacionalidad mensual: {context['avg_month_return']:.2%}\n"

    txt += f"\nResumen macro del día:\n{context['macro_text']}\n"

    txt += f"Score general (0–1): {context['overall_score']}\n"

    return txt
