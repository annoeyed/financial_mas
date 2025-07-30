import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from agents.base_agent import BaseAgent
from api.yfinance_api import get_bulk_volume_parallel, get_bulk_rsi_parallel
import re


class ScreeningAgent(BaseAgent):
    def __init__(self):
        super().__init__("ScreeningAgent")
        self.krx_path = "data/krx_stocks.csv"
        self.market_suffix = ".KS"

    async def handle(self, context: dict) -> dict:
        intent = context.get("intent", {})
        date_range = intent.get("date_range")
        date_str = intent.get("date")
        condition = intent.get("condition", {})
        limit = intent.get("limit", 10)

        try:
            # 날짜 파싱
            if date_range:
                prev_date = datetime.strptime(date_range["from"], "%Y-%m-%d").date()
                date = datetime.strptime(date_range["to"], "%Y-%m-%d").date()
            else:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                prev_date = date - timedelta(days=1)
            date_str = date.strftime("%Y-%m-%d")

            # 조건 파싱
            volume_threshold = self._parse_volume_change(condition.get("volume_change") or "0%")
            volume_direction = condition.get("volume_direction")
            rsi_threshold = condition.get("rsi")
            rsi_threshold = int(''.join(filter(str.isdigit, rsi_threshold))) if rsi_threshold else None

            if volume_direction not in ["up", "down"]:
                return {"error": "거래량 변화 방향(up/down)이 명확하지 않습니다."}

            # 종목 리스트 불러오기
            symbols, df_krx = self._get_filtered_symbols()

            # 병렬 수집
            volume_prev_map = get_bulk_volume_parallel(symbols, prev_date.strftime("%Y-%m-%d"), workers=3)
            volume_curr_map = get_bulk_volume_parallel(symbols, date.strftime("%Y-%m-%d"), workers=3)
            rsi_map = {}
            if rsi_threshold:
                rsi_map = get_bulk_rsi_parallel(symbols, date_str, workers=3)

            matched = []

            def volume_screening(symbol):
                try:
                    code = symbol.replace(".KS", "")
                    name = "Unknown"
                    if not df_krx.empty:
                        row = df_krx[df_krx["종목코드"] == code]
                        if not row.empty:
                            name = row.iloc[0]["회사명"]

                    vol_prev = volume_prev_map.get(symbol)
                    vol_curr = volume_curr_map.get(symbol)
                    if vol_prev is None or vol_curr is None or vol_prev == 0:
                        return None

                    pct_change = ((vol_curr / vol_prev) - 1) * 100
                    if (volume_direction == "up" and pct_change >= volume_threshold * 100) or \
                       (volume_direction == "down" and pct_change <= -volume_threshold * 100):

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
                except:
                    return None

            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(volume_screening, sym) for sym in symbols]
                for future in as_completed(futures):
                    res = future.result()
                    if res:
                        matched.append(res)
                        if len(matched) >= limit:
                            break

            # 응답 구성
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
            return {"error": f"[ScreeningAgent] 스크리닝 실패: {str(e)}"}

    def _parse_volume_change(self, text: str) -> float:
        if not text:
            return 0.0
        numbers = re.findall(r'\d+\.?\d*', text)
        return float(numbers[0]) / 100 if numbers else 0.0

    def _get_filtered_symbols(self, limit_symbols=50):
        try:
            df_krx = pd.read_csv(self.krx_path, encoding="euc-kr")
            df_krx = df_krx[~df_krx["회사명"].str.contains("스팩|리츠", na=False)]
            df_krx["상장일"] = pd.to_datetime(df_krx["상장일"], errors="coerce")
            df_krx = df_krx[df_krx["상장일"].dt.date < (datetime.now().date() - timedelta(days=90))]
            df_krx["종목코드"] = df_krx["종목코드"].astype(str).str.zfill(6)
            df_krx = df_krx[df_krx["종목코드"].str.match(r"^\d{6}$")]

            stable_symbols = [
                "005930", "000660", "035420", "051910", "006400",
                "035720", "207940", "068270", "323410", "051900",
                "006380", "017670", "015760", "028260", "032830",
                "086790", "055550", "105560", "139480", "024110"
            ]

            df_filtered = df_krx[df_krx["종목코드"].isin(stable_symbols)]
            symbols = [row["종목코드"] + self.market_suffix for _, row in df_filtered.iterrows()]
            return symbols, df_filtered

        except Exception as e:
            default_symbols = [
                "005930.KS", "000660.KS", "035420.KS", "051910.KS", "006400.KS",
                "035720.KS", "207940.KS", "068270.KS", "323410.KS", "051900.KS"
            ]
            return default_symbols, pd.DataFrame()