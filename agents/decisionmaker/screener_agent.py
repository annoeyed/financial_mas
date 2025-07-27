import pandas as pd
from datetime import datetime, timedelta
from api.koreainvestment_api import get_realtime_volume

class ScreeningAgent:
    def __init__(self):
        self.krx_path = "datapool/krx_stocks.csv"  # 종목코드 목록
        self.market_suffix = ""  # 한투는 접미사 필요 없음

    def handle(self, clarified_query: dict) -> dict:
        try:
            date_str = clarified_query["date"]  # '2025-07-24'
            condition = clarified_query.get("condition", {})
            volume_threshold = self._parse_volume_change(condition.get("volume_change", ""))  # 예: 3.0
            limit = clarified_query.get("limit", 10)

            volume_cond = condition.get("volume_change")
            rsi_cond = condition.get("rsi")

            if not volume_cond and not rsi_cond:
                return {"error": "스크리닝 조건이 필요합니다."}

            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            prev_date = date - timedelta(days=1)

            df_krx = pd.read_csv(self.krx_path, encoding="euc-kr")
            matched = []

            for _, row in df_krx.iterrows():
                if len(matched) >= limit:
                    break

                stock_code = str(row["종목코드"]).zfill(6)
                name = row["회사명"]

                try:
                    vol_prev, vol_curr = get_realtime_volume(stock_code, prev_date, date)
                    if vol_prev == 0:
                        continue

                    change_ratio = vol_curr / vol_prev
                    increase_pct = (change_ratio - 1) * 100

                    if increase_pct >= volume_threshold * 100:  # 예: 100% 이상 증가 조건
                        matched.append({
                            "name": name,
                            "code": stock_code,
                            "volume_yesterday": vol_prev,
                            "volume_today": vol_curr,
                            "change_ratio": round(increase_pct, 2)
                        })
                except Exception as e:
                    continue

            if not matched:
                return {
                    "judgment": [],
                    "judgment_summary": f"{date_str} 기준 전날 대비 거래량이 {int(volume_threshold*100)}% 이상 증가한 종목은 없습니다.",
                    "judgment_type": "screening"
                }

            return {
                "judgment": matched,
                "judgment_summary": f"{date_str} 기준 전날 대비 거래량이 {int(volume_threshold*100)}% 이상 증가한 종목 {len(matched)}개를 찾았습니다.",
                "judgment_type": "screening"
            }

        except Exception as e:
            return {
                "judgment": [],
                "error": str(e),
                "judgment_type": "screening"
            }

    def _parse_volume_change(self, text: str) -> float:
        if "%" in text:
            num = int(''.join(filter(str.isdigit, text)))
            return num / 100.0
        return 3.0  # 기본값
