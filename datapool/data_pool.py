from typing import Any, Dict

class DataPool:
    def __init__(self):
        self.market_data: Dict[str, Any] = {}
        self.rag_docs: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}

    # ---- 데이터 삽입 ----

    def set_market_data(self, source: str, symbol: str, data: dict):
        if source not in self.market_data:
            self.market_data[source] = {}
        self.market_data[source][symbol] = data

    def set_rag_docs(self, docs: dict):
        self.rag_docs = docs

    def set_metadata(self, key: str, value: Any):
        self.metadata[key] = value

    # ---- 데이터 접근 ----

    def get_price(self, symbol, date):
        if isinstance(symbol, dict):
            code = symbol.get("yfinance_code")
        else:
            code = symbol

        if not code:
            return None

        # 예시: self.market_data["yfinance"]["005930.KS"] = { "2025-07-25": { "price": 75300 } }
        for source in ["yfinance", "koreainvestment"]:
            source_data = self.market_data.get(source, {})
            symbol_data = source_data.get(code, {})
            if date in symbol_data:
                return symbol_data[date].get("price")  # 예: {'price': 75300}에서 price만 가져옴
        return None

    def get_volume(self, symbol, date: str) -> int:
        if isinstance(symbol, dict):
            code = symbol.get("yfinance_code")
        else:
            code = symbol

        if not code:
            return None

        for source in ["yfinance", "koreainvestment"]:
            source_data = self.market_data.get(source, {})
            symbol_data = source_data.get(code, {})
            if date in symbol_data:
                return symbol_data[date].get("volume")
        return None

    def get_rsi(self, symbol, date: str) -> float:
        if isinstance(symbol, dict):
            code = symbol.get("yfinance_code")
        else:
            code = symbol

        if not code:
            return None

        for source in ["yfinance", "koreainvestment"]:
            source_data = self.market_data.get(source, {})
            symbol_data = source_data.get(code, {})
            if date in symbol_data:
                return symbol_data[date].get("rsi")
        return None


    def get_doc_section(self, keyword: str) -> str:
        return self.rag_docs.get(keyword)

    def get_metadata(self, key: str) -> Any:
        return self.metadata.get(key)