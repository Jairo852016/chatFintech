# core/financial_data.py

import datetime as dt
from typing import Literal, Dict, Any

import pandas as pd
import yfinance as yf

from config import (
    SPY_TICKER,
    ALL_TICKERS,
    DEFAULT_PERIOD,
    DEFAULT_INTERVAL,
    VOLATILITY_WINDOW,
    MOMENTUM_WINDOW,
)

# ---------- FUNCIONES DE DESCARGA ----------

def download_history(
    ticker: str,
    period: str = DEFAULT_PERIOD,
    interval: str = DEFAULT_INTERVAL,
) -> pd.DataFrame:
    """
    Descarga datos históricos de yfinance para un ticker dado.
    Retorna un DataFrame con columnas típicas: Open, High, Low, Close, Adj Close, Volume.
    """
    df = yf.download(ticker, period=period, interval=interval, auto_adjust=False)
    # Aseguramos columna 'Date'
    df = df.reset_index()
    df.rename(columns={"Date": "date"}, inplace=True)
    return df


def download_all_tickers(
    tickers: list[str] = None,
    period: str = DEFAULT_PERIOD,
    interval: str = DEFAULT_INTERVAL,
) -> dict[str, pd.DataFrame]:
    """
    Descarga datos históricos para una lista de tickers y devuelve un diccionario:
    { 'SPY': df_Spy, 'AAPL': df_Aapl, ... }
    """
    if tickers is None:
        tickers = ALL_TICKERS

    data_dict: dict[str, pd.DataFrame] = {}
    for t in tickers:
        try:
            df = download_history(t, period=period, interval=interval)
            if not df.empty:
                data_dict[t] = df
        except Exception as e:
            print(f"Error descargando {t}: {e}")
    return data_dict


# ---------- INDICADORES BÁSICOS ----------

def add_returns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega columna 'ret' con rendimiento diario (Close).
    """
    df = df.copy()
    df["ret"] = df["Close"].pct_change()
    return df


def compute_volatility(
    df: pd.DataFrame,
    window: int = VOLATILITY_WINDOW,
    annualize: bool = True,
) -> float:
    """
    Calcula volatilidad realizada usando rendimientos diarios y ventana de 'window' días.
    Por defecto anualiza (multiplica por sqrt(252)).
    """
    df_ret = add_returns(df)
    last_window = df_ret["ret"].dropna().tail(window)
    if len(last_window) == 0:
        return float("nan")

    vol = last_window.std()
    if annualize:
        vol *= (252 ** 0.5)
    return float(vol)


def compute_momentum(df: pd.DataFrame, window: int = MOMENTUM_WINDOW) -> float:
    """
    Momentum simple: precio actual / precio de hace 'window' días - 1.
    """
    df = df.copy()
    if len(df) < window + 1:
        return float("nan")

    # Aseguramos que sean escalares (no Series)
    p_now = df["Close"].iloc[-1]           # scalar
    p_past = df["Close"].iloc[-(window+1)] # scalar

    val = p_now / p_past - 1.0
    return float(val)



def intraday_high_low(df: pd.DataFrame) -> dict:
    """
    Devuelve info del último día: open, high, low, close.
    Asume que df está ordenado por fecha.
    """
    if df.empty:
        return {}

    # Aseguramos que sea una fila, no un DataFrame de 1 fila
    # Si tenías last = df.tail(1), cámbialo por:
    last = df.iloc[-1]

    return {
        "date": last["date"],
        "open": float(last["Open"]),
        "high": float(last["High"]),
        "low": float(last["Low"]),
        "close": float(last["Close"]),
    }



# ---------- ESTACIONALIDAD ----------

def seasonality_by_month(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula estacionalidad mensual: rendimiento promedio por mes.
    Retorna un DataFrame con columnas ['month', 'avg_return', 'count'].
    """
    df_ret = add_returns(df)
    df_ret["month"] = df_ret["date"].dt.month
    grouped = (
        df_ret.groupby("month")["ret"]
        .agg(avg_return="mean", count="count")
        .reset_index()
        .sort_values("month")
    )
    return grouped


def seasonality_by_weekday(df: pd.DataFrame) -> pd.DataFrame:
    """
    Estacionalidad semanal: rendimiento promedio por día de la semana (0=Lunes, 4=Viernes).
    """
    df_ret = add_returns(df)
    df_ret["weekday"] = df_ret["date"].dt.weekday
    grouped = (
        df_ret.groupby("weekday")["ret"]
        .agg(avg_return="mean", count="count")
        .reset_index()
        .sort_values("weekday")
    )
    return grouped


def seasonality_by_month_day(df: pd.DataFrame) -> pd.DataFrame:
    """
    Estacionalidad por día del mes: rendimiento promedio por 'day of month' (1-31).
    Puede ser ruidoso, pero sirve como ejemplo.
    """
    df_ret = add_returns(df)
    df_ret["day"] = df_ret["date"].dt.day
    grouped = (
        df_ret.groupby("day")["ret"]
        .agg(avg_return="mean", count="count")
        .reset_index()
        .sort_values("day")
    )
    return grouped
