import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def get_nearest_trading_day_data(df: pd.DataFrame, target_date: str):
    target = pd.to_datetime(target_date).date() 
    df = df.copy()
    df = df.reset_index()
    df["Date"] = pd.to_datetime(df["Date"]).dt.date\

    future_dates = df[df["Date"] >= target]
    if future_dates.empty:
        return None

    return future_dates.iloc[0]

def get_nearest_trading_day(date: datetime.date) -> datetime.date:
    while date.weekday() >= 5:  # 5=토요일, 6=일요일
        date -= timedelta(days=1)
    return date

def get_price_data(symbol: str, date_str: str) -> float:
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    
        date = get_nearest_trading_day(date)
    
        start = (date - timedelta(days=1)).strftime("%Y-%m-%d")
        end = (date + timedelta(days=1)).strftime("%Y-%m-%d")

        df = yf.download(symbol, start=start, end=end, auto_adjust=False, progress=False)

        if df.empty:
            return None

        row = df[df.index.date == date]
        if row.empty:
            return None

        return float(row["Open"].values[0])
    except Exception as e:
        return None


def get_volume_data(symbol: str, date: str) -> int:
    """
    해당 날짜 또는 이후 가장 가까운 거래일의 거래량(volume)을 반환
    """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=date, end=(datetime.strptime(date, "%Y-%m-%d") + timedelta(days=7)).strftime("%Y-%m-%d"))

        if df.empty:
            return None

        nearest_row = get_nearest_trading_day_data(df, date)
        if nearest_row is None:
            return None

        return int(nearest_row["Volume"])
    except Exception as e:
        return None


def get_rsi_data(symbol: str, date: str, period: int = 14) -> float:
    """
    RSI (Relative Strength Index)를 계산해 해당 날짜의 값을 반환
    ※ yfinance는 RSI 직접 제공하지 않으므로 수동 계산
    """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="90d")  # 넉넉히 확보
        if df.empty or "Close" not in df.columns:
            return None

        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        nearest_row = get_nearest_trading_day_data(rsi.to_frame("RSI"), date)
        if nearest_row is None:
            return None

        return round(nearest_row["RSI"], 2)
    except Exception as e:
        return None