from agents.base_agent import BaseAgent
import yfinance as yf
from datetime import datetime, timedelta

class YFinanceDataAgent(BaseAgent):
    def __init__(self):
        super().__init__("YFinanceDataAgent")

    def process(self, structured_query: dict) -> dict:
        """
        structured_query 예시:
        {
            "target": "삼성전자",
            "date": "2024-07-01",
            "condition": "volume",
            "intent": "realtime_price_lookup"
        }
        """

        ticker = self.convert_name_to_ticker(structured_query.get("target"))
        if not ticker:
            return {"error": "해당 종목명을 티커로 변환할 수 없습니다."}

        try:
            data = self.call_api(self.fetch_data, ticker, structured_query.get("date"))
            return {"ticker": ticker, "data": data}
        except Exception as e:
            return {"error": str(e)}

    def convert_name_to_ticker(self, name: str) -> str:
        # 간단한 예시 맵핑 (실제 서비스에서는 DB나 API 필요)
        name_map = {
            "삼성전자": "005930.KS",
            "네이버": "035420.KQ",
            "카카오": "035720.KQ"
        }
        return name_map.get(name)

    def fetch_data(self, ticker: str, date: str = None) -> dict:
        # 기본적으로 30일치 데이터를 받아온 뒤, 날짜 필터
        end = datetime.today()
        start = end - timedelta(days=30)

        df = yf.download(ticker, start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"))

        if df.empty:
            raise ValueError("yfinance 데이터 없음")

        # 가장 최근 일자 또는 특정 날짜 선택
        if date:
            date = datetime.strptime(date, "%Y-%m-%d")
            df = df[df.index.date == date.date()]

        if df.empty:
            return {"message": "해당 날짜에 거래 데이터 없음"}

        row = df.iloc[-1]  # 마지막 행 기준
        return {
            "date": str(row.name.date()),
            "open": float(row["Open"]),
            "close": float(row["Close"]),
            "high": float(row["High"]),
            "low": float(row["Low"]),
            "volume": int(row["Volume"])
        }