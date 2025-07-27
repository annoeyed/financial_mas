import csv
import os
import difflib
import re

KRX_CSV_PATH = os.path.join(os.path.dirname(__file__), "../datapool/krx_stocks.csv")

class SymbolResolver:
    def __init__(self):
        self.symbol_map = {}
        self._load_csv()

    def _load_csv(self):
        with open(KRX_CSV_PATH, newline="", encoding="euc-kr") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row["회사명"].strip()
                code = row["종목코드"].zfill(6)
                market = row.get("시장구분", "").strip()

                if market == "KOSDAQ":
                    yfsuffix = ".KQ"
                else:
                    yfsuffix = ".KS"

                self.symbol_map[name] = {
                    "koreainvestment_code": code,
                    "yfinance_code": code + yfsuffix
                }

    def resolve(self, name: str) -> dict:
        name = name.strip()
        
        # '우선주' -> '우'로 단일화
        if name.endswith("우선주"):
            name = name.replace("우선주", "우")

        # 직매칭 우선
        result = self.symbol_map.get(name)
        if result:
            return result

        # 유사도 기반 매핑
        candidates = difflib.get_close_matches(name, self.symbol_map.keys(), n=1, cutoff=0.7)
        if candidates:
            return self.symbol_map[candidates[0]]

        return {}

# 전역 인스턴스
resolver = SymbolResolver()


# 종목명 추출 함수
def extract_symbol(text: str) -> dict:
    from utils.symbol_resolver import resolver
    import re

    candidates = re.findall(r"[가-힣A-Za-z0-9]{2,20}(?:우|우B|우선주)?", text)
    
    for word in candidates:
        word = word.strip()
        mapped = resolver.resolve(word)
        if mapped:
            return {
                "raw": word,
                **mapped
            }

    return {
        "raw": None,
        "error": "종목코드 매핑 실패"
    }
