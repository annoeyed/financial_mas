from api.yfinance_api import get_price_data, get_rsi_data, get_volume_data

def fetch_technical_data(symbol: dict, date: str) -> dict:
    if isinstance(symbol, dict):
        code = symbol.get("yfinance_code")
    else:
        code = symbol

    if not code:
        return {}

    price = get_price_data(code, date)
    volume = get_volume_data(code, date)
    rsi = get_rsi_data(code, date)

    return {
        "price": price,
        "volume": volume,
        "rsi": rsi
    }