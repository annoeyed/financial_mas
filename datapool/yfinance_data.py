from api.yfinance_api import get_price_data, get_rsi_data, get_volume_data

def fetch_technical_data(symbol: str, date: str) -> dict:
    """
    yfinance 기반 기술적 지표 수집
    - 시가, 거래량, RSI 등을 받아서 dict 형태로 가공
    """
    code = symbol.get("yfinance_code")

    if code is None or code == "":
        return {}
    
    if not symbol or "yfinance_code" not in symbol:
        return {}

    price=get_price_data(code, date)
    volume=get_volume_data(code, date)
    rsi=get_rsi_data(code, date)

    result = {
        "price": price,
        "volume": volume,
        "rsi": rsi
    }
    return result