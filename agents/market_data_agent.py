from .base_agent import BaseAgent
from tools.market_data_tools import fetch_stock_data

class MarketDataAgent(BaseAgent):
    def __init__(self):
        super().__init__("MarketDataAgent")

    async def process(self, query: str) -> dict:
        # 예시: query에서 종목명이나 날짜 추출
        params = {"query": query}
        data = await self.call_api(fetch_stock_data, params)
        return {"agent": self.name, "data": data}
