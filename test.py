from api.yfinance_api import get_volume_data

test_cases = [
    ("005930.KS", "2025-07-19"),  # 삼성전자
    ("000660.KS", "2025-07-19"),  # SK하이닉스
    ("035720.KQ", "2025-07-19"),  # 카카오
    ("000250.KQ", "2025-07-19"),  # 삼천당제약 (코스닥)
]

for code, date in test_cases:
    vol = get_volume_data(code, date)
    print(f"{code} ({date}) → {vol}")
