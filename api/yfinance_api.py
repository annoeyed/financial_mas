import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random
from utils.cache_manager import CacheManager

# 전역 캐시 매니저 인스턴스
cache_manager = CacheManager()

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

def safe_yf_download(symbol: str, start: str, end: str, max_retries: int = 3):
    """안전한 YFinance 다운로드 with 재시도 로직"""
    for attempt in range(max_retries):
        try:
            # API 리밋 방지를 위한 지연시간
            time.sleep(random.uniform(0.1, 0.3))
            df = yf.download(symbol, start=start, end=end, auto_adjust=False, progress=False, threads=False)
            return df
        except Exception as e:
            if attempt < max_retries - 1:
                # 재시도 전 더 긴 지연시간
                time.sleep(random.uniform(1, 3))
                continue
            else:
                return pd.DataFrame()
    return pd.DataFrame()

def get_price_data(symbol: str, date_str: str) -> float:
    try:
        # 캐시에서 먼저 확인
        cached_data = cache_manager.get("price", symbol, date_str)
        if cached_data is not None:
            return cached_data
        
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    
        date = get_nearest_trading_day(date)
    
        start = (date - timedelta(days=1)).strftime("%Y-%m-%d")
        end = (date + timedelta(days=1)).strftime("%Y-%m-%d")

        df = safe_yf_download(symbol, start, end)

        if df.empty:
            return None

        row = df[df.index.date == date]
        if row.empty:
            return None

        result = float(row["Open"].values[0])
        
        # 결과를 캐시에 저장
        cache_manager.set("price", symbol, date_str, result)
        
        return result
    except Exception as e:
        return None


def get_volume_data(symbol: str, date: str) -> int:
    """
    지정된 날짜 또는 그 이후 가장 가까운 거래일의 거래량을 반환
    """
    try:
        # 캐시에서 먼저 확인
        cached_data = cache_manager.get("volume", symbol, date)
        if cached_data is not None:
            return cached_data
        
        ticker = yf.Ticker(symbol)
        end_date = (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=7)).strftime("%Y-%m-%d")
        
        # API 리밋 방지를 위한 지연시간
        time.sleep(random.uniform(0.1, 0.2))
        df = ticker.history(start=date, end=end_date)

        if df.empty:
            return None

        nearest_row = get_nearest_trading_day_data(df, date)
        if nearest_row is None:
            return None

        result = int(nearest_row["Volume"])
        
        # 결과를 캐시에 저장
        cache_manager.set("volume", symbol, date, result)
        
        return result
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

def get_bulk_volume_parallel(symbols, target_date, workers=10):
    """API 리밋을 고려한 안전한 병렬 처리"""
    start = (datetime.strptime(target_date, "%Y-%m-%d") - timedelta(days=2)).strftime("%Y-%m-%d")
    end = (datetime.strptime(target_date, "%Y-%m-%d") + timedelta(days=2)).strftime("%Y-%m-%d")
    target_dt = datetime.strptime(target_date, "%Y-%m-%d").date()

    result = {}

    def fetch(symbol):
        try:
            # 캐시에서 먼저 확인
            cached_data = cache_manager.get("volume", symbol, target_date)
            if cached_data is not None:
                return symbol, cached_data
            
            # API 리밋 방지를 위한 지연시간
            time.sleep(random.uniform(0.2, 0.5))
            df = safe_yf_download(symbol, start, end)
            if df.empty or "Volume" not in df:
                return symbol, None
            df = df.reset_index()
            df["Date"] = pd.to_datetime(df["Date"]).dt.date
            nearest = df[df["Date"] >= target_dt]
            if nearest.empty:
                return symbol, None
            
            volume = int(nearest.iloc[0]["Volume"].item())
            
            # 결과를 캐시에 저장
            cache_manager.set("volume", symbol, target_date, volume)
            
            return symbol, volume
        except Exception as e:
            return symbol, None

    # 워커 수를 줄여서 API 리밋 방지
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(fetch, symbol) for symbol in symbols]
        for future in as_completed(futures):
            symbol, volume = future.result()
            if volume is not None:
                result[symbol] = volume

    return result

def get_rsi_data(symbol: str, date: str, period: int = 14) -> float:
    """
    지정된 날짜의 RSI 값을 계산
    """
    try:
        # 캐시에서 먼저 확인
        cached_data = cache_manager.get("rsi", symbol, date, period=period)
        if cached_data is not None:
            return cached_data
        
        ticker = yf.Ticker(symbol)
        end_date = (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=7)).strftime("%Y-%m-%d")
        
        # API 리밋 방지를 위한 지연시간
        time.sleep(random.uniform(0.1, 0.2))
        df = ticker.history(start=date, end=end_date)

        if df.empty:
            return None

        nearest_row = get_nearest_trading_day_data(df, date)
        if nearest_row is None:
            return None

        # RSI 계산을 위한 더 많은 데이터 필요
        start_date = (datetime.strptime(date, "%Y-%m-%d") - timedelta(days=period + 10)).strftime("%Y-%m-%d")
        time.sleep(random.uniform(0.1, 0.2))
        df_rsi = ticker.history(start=start_date, end=end_date)
        
        if len(df_rsi) < period:
            return None

        # RSI 계산
        delta = df_rsi['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        nearest_idx = df_rsi[df_rsi.index.date >= datetime.strptime(date, "%Y-%m-%d").date()].index
        if len(nearest_idx) == 0:
            return None
        
        result = float(rsi.iloc[-1])
        
        # 결과를 캐시에 저장
        cache_manager.set("rsi", symbol, date, result, period=period)
        
        return result
    except Exception:
        return None

def get_bulk_rsi_parallel(symbols, target_date: str, period=14, workers=10) -> dict:
    """API 리밋을 고려한 안전한 RSI 병렬 처리"""
    result = {}

    def fetch(symbol):
        try:
            # 캐시에서 먼저 확인
            cached_data = cache_manager.get("rsi", symbol, target_date, period=period)
            if cached_data is not None:
                return symbol, cached_data
            
            # API 리밋 방지를 위한 지연시간
            time.sleep(random.uniform(0.3, 0.6))
            rsi = get_rsi_data(symbol, target_date, period)
            return symbol, rsi
        except Exception as e:
            return symbol, None

    # 워커 수를 줄여서 API 리밋 방지
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(fetch, symbol) for symbol in symbols]
        for future in as_completed(futures):
            symbol, rsi = future.result()
            if rsi is not None:
                result[symbol] = rsi

    return result