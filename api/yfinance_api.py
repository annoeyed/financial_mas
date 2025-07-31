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
    
    target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    start_date = (target_date - timedelta(days=5)).strftime("%Y-%m-%d")
    end_date = (target_date + timedelta(days=5)).strftime("%Y-%m-%d")

    try:
        df = yf.download(symbol, start=start_date, end=end_date, auto_adjust=False, progress=False, threads=False)
        if df.empty:
            return None

        df = df.reset_index()
        df["Date"] = pd.to_datetime(df["Date"]).dt.date

        future_dates = df[df["Date"] >= target_date]
        if future_dates.empty:
            return None

        row = future_dates.iloc[0]
        return float(row["Close"])

    except Exception as e:
        return None

def get_moving_average_data(symbol: str, date_str: str, period: int = 50) -> dict:
    """
    지정된 날짜의 이동평균과 현재가를 계산
    """
    try:
        # 캐시에서 먼저 확인
        cached_data = cache_manager.get("moving_average", symbol, date_str, period=period)
        if cached_data is not None:
            return cached_data
        
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        # 이동평균 계산을 위한 충분한 데이터 수집 (period + 30일)
        start_date = (date - timedelta(days=period + 50)).strftime("%Y-%m-%d")
        end_date = (date + timedelta(days=10)).strftime("%Y-%m-%d")
        
        # API 리밋 방지를 위한 지연시간
        time.sleep(random.uniform(0.2, 0.4))
        
        df = yf.download(symbol, start=start_date, end=end_date, auto_adjust=False, progress=False, threads=False)
        
        if df.empty or len(df) < period:
            print(f"데이터 부족: {len(df)}행 (필요: {period}행)")
            return None
        
        close_col = df['Close']
        if isinstance(close_col, pd.DataFrame):
            close_col = close_col.iloc[:, 0]
        
        # 이동평균 계산
        df['MA'] = close_col.rolling(window=period).mean()
        
        # 지정된 날짜의 데이터 찾기
        target_date = pd.to_datetime(date_str).date()
        nearest_data = None
        
        for idx, row in df.iterrows():
            if idx.date() >= target_date:
                nearest_data = row
                break
        
        if nearest_data is None or pd.isna(nearest_data['MA'].iloc[0]):
            return None
        
        current_price = float(nearest_data['Close'].iloc[0])
        moving_average = float(nearest_data['MA'].iloc[0])

        
        # 돌파율 계산
        breakout_ratio = ((current_price - moving_average) / moving_average) * 100
        
        result = {
            'current_price': current_price,
            'moving_average': moving_average,
            'breakout_ratio': round(breakout_ratio, 2),
            'is_breakout': breakout_ratio > 10  # 10% 이상 상향 돌파
        }
        
        # 결과를 캐시에 저장
        cache_manager.set("moving_average", symbol, date_str, result, period=period)
        
        return result
        
    except Exception as e:
        print(f"이동평균 계산 오류: {e}")
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
    except Exception as e:
        print(f"[ERROR] get_price_data() Exception: {e}", flush=True)
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

def get_bulk_moving_average_parallel(symbols, target_date: str, period=50, workers=5) -> dict:
    """API 리밋을 고려한 안전한 이동평균 병렬 처리"""
    result = {}

    def fetch(symbol):
        try:
            # 캐시에서 먼저 확인
            cached_data = cache_manager.get("moving_average", symbol, target_date, period=period)
            if cached_data is not None:
                return symbol, cached_data
            
            # API 리밋 방지를 위한 지연시간
            time.sleep(random.uniform(0.5, 1.0))
            ma_data = get_moving_average_data(symbol, target_date, period)
            return symbol, ma_data
        except Exception as e:
            return symbol, None

    # 워커 수를 줄여서 API 리밋 방지
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(fetch, symbol) for symbol in symbols]
        for future in as_completed(futures):
            symbol, ma_data = future.result()
            if ma_data is not None:
                result[symbol] = ma_data

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