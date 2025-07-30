import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import yfinance as yf
from api.yfinance_api import get_bulk_volume_parallel, get_bulk_rsi_parallel

class ScreeningAgent:
    def __init__(self):
        self.krx_path = "datapool/krx_stocks.csv"
        self.market_suffix = ".KS"

    def handle(self, clarified_query: dict) -> dict:
        try:
            date_range = clarified_query.get("date_range")
            if date_range:
                prev_date = datetime.strptime(date_range["from"], "%Y-%m-%d").date()
                date = datetime.strptime(date_range["to"], "%Y-%m-%d").date()
            else:
                date = datetime.strptime(clarified_query["date"], "%Y-%m-%d").date()
                prev_date = date - timedelta(days=1)

            date_str = date.strftime("%Y-%m-%d")
            volume_threshold = self._parse_volume_change(
                clarified_query.get("condition", {}).get("volume_change") or "0%"
            )
            volume_direction = clarified_query.get("condition", {}).get("volume_direction")
            rsi_threshold = clarified_query.get("condition", {}).get("rsi")  # ← 추가
            rsi_threshold = int(''.join(filter(str.isdigit, rsi_threshold))) if rsi_threshold else None  # ← 추가
            limit = clarified_query.get("limit", 10)

            if volume_direction not in ["up", "down"]:
                return {"error": "거래량 변화 방향(up/down)이 명확하지 않습니다."}

            df_krx = pd.read_csv(self.krx_path, encoding="euc-kr")
            df_krx = df_krx[~df_krx["회사명"].str.contains("스팩|리츠", na=False)]

            df_krx["상장일"] = pd.to_datetime(df_krx["상장일"], errors="coerce")
            df_krx = df_krx[df_krx["상장일"].dt.date < (datetime.now().date() - timedelta(days=90))]
            df_krx["종목코드"] = df_krx["종목코드"].astype(str).str.zfill(6)
            df_krx = df_krx[df_krx["종목코드"].str.match(r"^\d{6}$")]

            symbols = [row["종목코드"] + self.market_suffix for _, row in df_krx.iterrows()]

            volume_prev_map = get_bulk_volume_parallel(symbols, prev_date.strftime("%Y-%m-%d"))
            volume_curr_map = get_bulk_volume_parallel(symbols, date.strftime("%Y-%m-%d"))
            rsi_map = get_bulk_rsi_parallel(symbols, date_str) if rsi_threshold else {}  # ← 추가

            matched = []

            def volume_screening(row):
                code = str(row["종목코드"]).zfill(6)
                symbol = code + self.market_suffix
                name = row["회사명"]
                vol_prev = volume_prev_map.get(symbol)
                vol_curr = volume_curr_map.get(symbol)

                if vol_prev is None or vol_curr is None or vol_prev == 0:
                    return None

                pct_change = ((vol_curr / vol_prev) - 1) * 100
                if (volume_direction == "up" and pct_change >= volume_threshold * 100) or \
                   (volume_direction == "down" and pct_change <= -volume_threshold * 100):

                    # RSI 조건 확인
                    if rsi_threshold:
                        rsi = rsi_map.get(symbol)
                        if rsi is None or rsi < rsi_threshold:
                            return None
                    else:
                        rsi = None

                    return {
                        "name": name,
                        "code": code,
                        "volume_yesterday": vol_prev,
                        "volume_today": vol_curr,
                        "change_ratio": round(pct_change, 2),
                        **({"rsi": rsi} if rsi_threshold else {})
                    }
                return None

            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = [executor.submit(volume_screening, row) for _, row in df_krx.iterrows()]
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        matched.append(result)
                        if len(matched) >= limit:
                            break

            direction_kor = "증가" if volume_direction == "up" else "감소"
            summary = f"{date_str} 기준 전날 대비 거래량이 {int(volume_threshold * 100)}% 이상 {direction_kor}한 종목"
            if rsi_threshold:
                summary += f", RSI가 {rsi_threshold} 이상인 종목"

            return {
                "judgment": matched,
                "judgment_summary": f"{summary} {len(matched)}개를 찾았습니다." if matched else f"{summary}은 없습니다.",
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
        return 0.3  # 기본값 (30%)