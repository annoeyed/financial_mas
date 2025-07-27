from api.koreainvestment_api import get_realtime_price, get_realtime_volume

def fetch_market_data(symbol: str, date: str) -> dict:
    price = get_realtime_price(symbol)
    volume = get_realtime_volume(symbol)

    if price is None or price == 0.0:
        price = None
    if volume is None or volume == 0:
        volume = None

    return {
        "price": price,
        "volume": volume
    }