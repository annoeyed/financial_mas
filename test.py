from api.koreainvestment_api import get_realtime_volume
from datetime import datetime, timedelta
import pandas as pd

target_date = datetime(2025, 4, 20).date()
prev_date = datetime(2025, 4, 18).date()  # 토,일 제외
threshold = 1.1  # 10% 증가

krx = pd.read_csv("datapool/krx_stocks.csv", encoding="euc-kr")

for _, row in krx.iterrows():
    code = str(row["종목코드"]).zfill(6)
    name = row["회사명"]
    try:
        v_prev, v_curr = get_realtime_volume(code, prev_date, target_date)
        if v_prev == 0:
            continue
        ratio = v_curr / v_prev
        if ratio >= threshold:
            print(f"{name} ({code}): {v_prev} → {v_curr} ({round(ratio, 2)}배)")
    except Exception as e:
        continue
