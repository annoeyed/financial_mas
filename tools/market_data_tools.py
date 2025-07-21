# 종목 리스트 자동 수집 
import pandas as pd

def get_nasdaq_tickers():
    url = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
    df = pd.read_csv(url, sep='|')
    tickers = df['Symbol'].tolist()
    return [t for t in tickers if t.isalpha()]

# 기존 함수에서 tickers를 이 함수로 대체
def get_top_rising_stocks(n=5):
    tickers = get_nasdaq_tickers()[:50]  # 속도 문제로 50개만 예시

import yfinance as yf

def get_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        return float(stock.history(period="1d")['Close'].iloc[-1])
    except Exception as e:
        return f"가격 조회 실패: {e}"

def get_top_volume_stocks(n=10):
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']  # 실제로는 전체 리스트 필요
    volumes = []
    for t in tickers:
        try:
            stock = yf.Ticker(t)
            vol = stock.history(period="1d")['Volume'].iloc[-1]
            volumes.append((t, int(vol)))
        except Exception:
            continue
    return sorted(volumes, key=lambda x: x[1], reverse=True)[:n]

def get_stocks_by_condition(percent):
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    result = []
    for t in tickers:
        try:
            stock = yf.Ticker(t)
            hist = stock.history(period="2d")
            if len(hist) < 2:
                continue
            prev, curr = hist['Volume'].iloc[0], hist['Volume'].iloc[1]
            if prev == 0:
                continue
            change = ((curr - prev) / prev) * 100
            if change >= percent:
                result.append((t, float(change)))
        except Exception:
            continue
    return result

def get_signal_stocks(ma_days=50, percent=10):
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    result = []
    for t in tickers:
        try:
            stock = yf.Ticker(t)
            hist = stock.history(period=f"{ma_days+1}d")
            if len(hist) < ma_days:
                continue
            ma = hist['Close'].rolling(ma_days).mean().iloc[-1]
            curr = hist['Close'].iloc[-1]
            if ma == 0:
                continue
            change = ((curr - ma) / ma) * 100
            if change >= percent:
                result.append((t, float(change)))
        except Exception:
            continue
    return result

def get_top_rising_stocks(n=5):
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    changes = []
    for t in tickers:
        try:
            stock = yf.Ticker(t)
            hist = stock.history(period="2d")
            if len(hist) < 2:
                continue
            prev, curr = hist['Close'].iloc[0], hist['Close'].iloc[1]
            if prev == 0:
                continue
            change = ((curr - prev) / prev) * 100
            if change > 0:  # 양수(오른 종목)만 추가
                changes.append((t, float(change)))
        except Exception:
            continue
    return sorted(changes, key=lambda x: x[1], reverse=True)[:n]

def get_top_falling_stocks(n=5):
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    changes = []
    for t in tickers:
        try:
            stock = yf.Ticker(t)
            hist = stock.history(period="2d")
            if len(hist) < 2:
                continue
            prev, curr = hist['Close'].iloc[0], hist['Close'].iloc[1]
            if prev == 0:
                continue
            change = ((curr - prev) / prev) * 100
            if change < 0:  # 음수(떨어진 종목)만 추가
                changes.append((t, float(change)))
        except Exception:
            continue
    return sorted(changes, key=lambda x: x[1])[:n]
