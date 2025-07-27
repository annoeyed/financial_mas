from agents.base_agent import BaseAgent
from datapool import yfinance_data, koreaninvestment_data

class DataProviderAgent(BaseAgent):
    def __init__(self):
        super().__init__("DataProviderAgent")

    def handle(self, parsed_query: dict, data_pool):
        symbol = parsed_query.get("symbol")
        date = parsed_query.get("date")
        keyword = parsed_query.get("keyword")

        if symbol and date:
            # yfinance 우선 수집
            yf_data = yfinance_data.fetch_technical_data(symbol, date)
            yf_code = symbol.get("yfinance_code")
            if yf_data.get("price"):
                data_pool.set_market_data("yfinance", yf_code, {date: yf_data})


            # 보완적으로 한투도 시도
            ki_code = symbol.get("koreainvestment_code")
            ki_data = koreaninvestment_data.fetch_market_data(ki_code, date)
            if ki_data.get("price") and yf_code not in data_pool.market_data.get("yfinance", {}):
                data_pool.set_market_data("koreainvestment", ki_code, {date: ki_data})