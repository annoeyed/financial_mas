import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_nearest_trading_day_data(df: pd.DataFrame, target_date: str):
    target = pd.to_datetime(target_date).date() 
    df = df.copy()
    df = df.reset_index()
    df["Date"] = pd.to_datetime(df["Date"]).dt.date

    future_dates = df[df["Date"] >= target]
    if future_dates.empty:
        return None

    return future_dates.iloc[0]

def get_nearest_trading_day(date: datetime.date) -> datetime.date:
    while date.weekday() >= 5:
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
    지정된 날짜 또는 그 이후 가장 가까운 거래일의 거래량을 반환
    """
    try:
        ticker = yf.Ticker(symbol)
        end_date = (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=7)).strftime("%Y-%m-%d")
        df = ticker.history(start=date, end=end_date)

        if df.empty:
            return None

        nearest_row = get_nearest_trading_day_data(df, date)
        if nearest_row is None:
            return None

        return int(nearest_row["Volume"])
    except Exception:
        return None 

def get_volume_change(symbol: str, prev_date: str, date: str) -> dict:
    """
    두 날짜의 거래량을 비교하여 변화율을 계산
    """
    vol_prev = get_volume_data(symbol, prev_date)
    vol_curr = get_volume_data(symbol, date)

    if vol_prev is None or vol_curr is None or vol_prev == 0:
        return {"error": "거래량 정보 부족"}

    change_ratio = vol_curr / vol_prev
    increase_pct = (change_ratio - 1) * 100

    return {
        "volume_yesterday": vol_prev,
        "volume_today": vol_curr,
        "change_ratio": round(increase_pct, 2)
    }    

def get_bulk_volume_parallel(symbols, target_date, workers=20):
    start = (datetime.strptime(target_date, "%Y-%m-%d") - timedelta(days=2)).strftime("%Y-%m-%d")
    end = (datetime.strptime(target_date, "%Y-%m-%d") + timedelta(days=2)).strftime("%Y-%m-%d")
    target_dt = datetime.strptime(target_date, "%Y-%m-%d").date()

    result = {}

    def fetch(symbol):
        try:
            df = yf.download(symbol, start=start, end=end, auto_adjust=False, progress=False, threads=False)
            if df.empty or "Volume" not in df:
                return symbol, None
            df = df.reset_index()
            df["Date"] = pd.to_datetime(df["Date"]).dt.date
            nearest = df[df["Date"] >= target_dt]
            if nearest.empty:
                return symbol, None
            volume = nearest.iloc[0]["Volume"]
            return symbol, int(volume.item() if hasattr(volume, "item") else volume)
        except Exception:
            return symbol, None

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(fetch, symbol): symbol for symbol in symbols}
        for future in as_completed(futures):
            symbol, volume = future.result()
            if volume is not None:
                result[symbol] = volume

    return result

def get_rsi_data(symbol: str, date: str, period: int = 14) -> float:
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="90d")
        if df.empty or "Close" not in df.columns:
            return None
        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        rsi_df = pd.DataFrame({"Date": rsi.index, "RSI": rsi.values})
        nearest_row = get_nearest_trading_day_data(rsi_df, date)
        return round(nearest_row["RSI"], 2) if nearest_row is not None else None
    except Exception:
        return None
    
def get_bulk_rsi_parallel(symbols, target_date: str, period=14, workers=20) -> dict:
    result = {}

    def fetch(symbol):
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="90d")
            if df.empty or "Close" not in df.columns:
                return symbol, None
            delta = df["Close"].diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            avg_gain = gain.rolling(window=period).mean()
            avg_loss = loss.rolling(window=period).mean()
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            rsi_df = pd.DataFrame({"Date": rsi.index, "RSI": rsi.values})
            nearest_row = get_nearest_trading_day_data(rsi_df, target_date)
            return symbol, round(nearest_row["RSI"], 2) if nearest_row is not None else None
        except:
            return symbol, None

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(fetch, s): s for s in symbols}
        for future in as_completed(futures):
            symbol, rsi_val = future.result()
            if rsi_val is not None:
                result[symbol] = rsi_val

    return result