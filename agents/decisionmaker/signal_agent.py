import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from agents.base_agent import BaseAgent
from api.yfinance_api import get_bulk_moving_average_parallel


class SignalAgent(BaseAgent):
    def __init__(self):
        super().__init__("SignalAgent")
        self.krx_path = "data/krx_stocks.csv"
        self.market_suffix = ".KS"

    async def handle(self, context: dict) -> dict:
        intent = context.get("intent", {})
        date_str = intent.get("date")
        period = intent.get("period", 50)
        breakout_threshold = intent.get("threshold", 10)
        limit = intent.get("limit", 10)

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            date_str = date.strftime("%Y-%m-%d")

            # 종목 목록 가져오기
            symbols, df_krx = self._get_filtered_symbols()

            # 이동평균 계산
            ma_data_map = get_bulk_moving_average_parallel(symbols, date_str, period=period, workers=3)

            matched = []

            def signal_screening(symbol):
                try:
                    code = symbol.replace(".KS", "")
                    name = "Unknown"
                    if not df_krx.empty:
                        row = df_krx[df_krx["종목코드"] == code]
                        if not row.empty:
                            name = row.iloc[0]["회사명"]

                    ma_data = ma_data_map.get(symbol)
                    if not ma_data:
                        return None

                    if ma_data["is_breakout"] and ma_data["breakout_ratio"] >= breakout_threshold:
                        return {
                            "name": name,
                            "code": code,
                            "current_price": ma_data["current_price"],
                            "moving_average": ma_data["moving_average"],
                            "breakout_ratio": round(ma_data["breakout_ratio"], 2)
                        }
                    return None
                except:
                    return None

            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(signal_screening, s) for s in symbols]
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        matched.append(result)
                        if len(matched) >= limit:
                            break

            matched.sort(key=lambda x: x["breakout_ratio"], reverse=True)

            summary = f"{date_str} 기준 {period}일 이동평균선을 {breakout_threshold}% 이상 상향 돌파한 종목"

            return {
                "judgment": matched,
                "judgment_summary": f"{summary} {len(matched)}개를 찾았습니다." if matched else f"{summary}은 없습니다.",
                "judgment_type": "signal_detection"
            }

        except Exception as e:
            return {"error": f"[SignalAgent] 시그널 감지 실패: {str(e)}"}

    def _get_filtered_symbols(self, limit_symbols=20):
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

        except Exception:
            default_symbols = [
                "005930.KS", "000660.KS", "035420.KS", "051910.KS", "006400.KS",
                "035720.KS", "207940.KS", "068270.KS", "323410.KS", "051900.KS"
            ]
            return default_symbols, pd.DataFrame()