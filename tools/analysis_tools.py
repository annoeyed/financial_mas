async def compute_indicators(params: dict) -> dict:
    # 이동평균, RSI 등 계산 로직
    return {"ma": 123.4, "rsi": 56.7}

async def screen_stocks(params: dict) -> list:
    # 조건에 맞춰 스크리닝
    return [{"ticker": "AAPL", "score": 0.95}]

async def detect_signals(params: dict) -> list:
    # 시그널 감지 로직
    return [{"ticker": "TSLA", "signal": "breakout"}]
