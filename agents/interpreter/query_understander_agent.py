from agents.base_agent import BaseAgent
from utils.symbol_resolver import extract_symbol
import re
from datetime import datetime, timedelta

class QueryUnderstanderAgent(BaseAgent):
    def __init__(self):
        super().__init__("QueryUnderstanderAgent")

    def get_most_recent_trading_day(self, reference: datetime = None) -> str:
        if reference is None:
            reference = datetime.today()
        weekday = reference.weekday()
        if weekday == 5:  # 토요일
            reference -= timedelta(days=1)
        elif weekday == 6:  # 일요일
            reference -= timedelta(days=2)
        return reference.strftime("%Y-%m-%d")

    def handle(self, text: str) -> dict:
        if not isinstance(text, str):
            raise TypeError(f"[QueryUnderstanderAgent] handle() expects a string, got {type(text)}")

        result = {}
        text = text.strip()

        # 0. intent 분기
        is_screening = self._is_screening_intent(text)

        # 1. 날짜 추출
        if "오늘" in text or "지금" in text or "현재" in text:
            result["date"] = self.get_most_recent_trading_day()
        else:
            date_match = re.search(r"\d{4}[-./]\d{1,2}[-./]\d{1,2}", text)
            if date_match:
                try:
                    normalized = date_match.group().replace(".", "-").replace("/", "-")
                    parsed_date = datetime.strptime(normalized, "%Y-%m-%d").date()
                    result["date"] = parsed_date.strftime("%Y-%m-%d")
                except ValueError as ve:
                    print(f"[DEBUG] 날짜 파싱 실패: {ve}")
            else:
                print("[DEBUG] 날짜 패턴 없음")

        # 2. 종목 추출 (lookup일 때만)
        if not is_screening:
            symbol = extract_symbol(text)
            if isinstance(symbol, dict):
                result["symbol"] = symbol
            elif isinstance(symbol, str):
                result["symbol"] = {
                    "raw": symbol,
                    "koreainvestment_code": None,
                    "yfinance_code": None
                }
            else:
                result["symbol"] = {"raw": None, "error": "종목코드 매핑 실패"}
       
        # 3. 조건 추출
        condition = {}

        # RSI 조건
        if "RSI" in text.upper():
            rsi_match = re.search(r'RSI.*?(\d+)', text, re.IGNORECASE)
            if rsi_match:
                condition["rsi"] = f">{rsi_match.group(1)}"

        # 거래량 조건
        if "거래량" in text and ("증가" in text or "늘어난" in text or "%" in text):
            volume_match = re.search(r'(\d+)\s*[%퍼센트]', text)
            if volume_match:
                condition["volume_change"] = f">{volume_match.group(1)}%"

        result["condition"] = condition

        # 4. 개수 제한 추출
        limit_match = re.search(r"(\d+)\s*(개|종목)", text)
        if limit_match:
            result["limit"] = int(limit_match.group(1))
  
        if is_screening:
                result["condition"] = condition
        
        return result

    def _is_screening_intent(self, text: str) -> bool:
        """
        symbol이 명시되지 않고 '조건'이나 '스캔' 같은 표현이 있을 경우 스크리닝으로 판단.
        """
        screening_patterns = ["이상", "미만", "상위", "하위", "증가", "급등", "종목", "퍼센트", "비율", "전날 대비", "조건", "검색"]
        return any(kw in text for kw in screening_patterns)