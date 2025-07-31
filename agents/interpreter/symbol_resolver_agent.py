from agents.base_agent import BaseAgent
import csv
import os
import difflib
import re

KRX_CSV_PATH = os.path.join(os.path.dirname(__file__), "../../data/krx_stocks.csv")

class SymbolResolverAgent(BaseAgent):
    def __init__(self):
        super().__init__("SymbolResolverAgent")
        self.symbol_map = {}
        self._load_csv()

    def _load_csv(self):
        with open(KRX_CSV_PATH, newline="", encoding="euc-kr") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row["회사명"].strip()
                code = row["종목코드"].zfill(6)
                market = row.get("시장구분", "").strip()

                yfsuffix = ".KQ" if market == "KOSDAQ" else ".KS"

                self.symbol_map[name] = {
                    "yfinance_code": code + yfsuffix
                }

    def resolve(self, name: str) -> dict:
        name = name.strip()
        if name.endswith("우선주"):
            name = name.replace("우선주", "우")

        result = self.symbol_map.get(name)
        if result:
            return result
        if not result:
            return {
                "raw": name,
                "error": "종목코드 매핑 실패"
            }

        candidates = difflib.get_close_matches(name, self.symbol_map.keys(), n=1, cutoff=0.7)
        if candidates:
            return self.symbol_map[candidates[0]]

        return {}

    async def handle(self, context: dict) -> dict:
        text = context.get("query", "")
        candidates = re.findall(r"[가-힣A-Za-z0-9]{2,20}(?:우|우B|우선주)?", text)

        filtered = [word for word in candidates if not word.isdigit()]
        for word in filtered:
            word = word.strip()
            mapped = self.resolve(word)
            if mapped:
                context["symbol"] = {
                    "raw": word,
                    **mapped
                }
                return context

        for word in candidates:
            word = word.strip()
            mapped = self.resolve(word)
            if mapped:
                context["symbol"] = {
                    "raw": word,
                    **mapped
                }
                return context

        context["symbol"] = {
            "raw": None,
            "error": "종목코드 매핑 실패"
        }
        return context