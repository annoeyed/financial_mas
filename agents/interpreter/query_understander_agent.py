from agents.base_agent import BaseAgent
from agents.interpreter.symbol_resolver_agent import SymbolResolverAgent
from dateutil.relativedelta import relativedelta
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

    async def handle(self, context: dict) -> dict:
        text = context.get("query", "")
        if not isinstance(text, str):
            raise TypeError(f"[QueryUnderstanderAgent] query must be a string, got {type(text)}")

        result = {}
        text = text.strip()

        # 0. intent 분기
        is_screening = self._is_screening_intent(text)

        # 1. 날짜 추출
        date_keywords = {"오늘": 0, "어제": 1, "그저께": 2, "3일 전": 3, "4일 전": 4, "5일 전": 5, "6일 전": 6, "일주일 전": 7}
        weekday_map = {"월요일": 0, "화요일": 1, "수요일": 2, "목요일": 3, "금요일": 4, "토요일": 5, "일요일": 6}
        date_found = False

        for keyword, days_ago in date_keywords.items():
            if keyword in text:
                ref = datetime.today() - timedelta(days=days_ago)
                result["date"] = self.get_most_recent_trading_day(ref)
                date_found = True
                break

        if "어제" in text and "그저께" in text:
            to_date = self.get_most_recent_trading_day(datetime.today() - timedelta(days=1))
            from_date = self.get_most_recent_trading_day(datetime.today() - timedelta(days=2))
            result["date_range"] = {"from": from_date, "to": to_date}
            date_found = True

        if not date_found:
            match = re.search(r"지난주\s*(월요일|화요일|수요일|목요일|금요일|토요일|일요일)", text)
            if match:
                target_weekday = weekday_map[match.group(1)]
                one_week_ago = datetime.today() - timedelta(days=7)
                last_week_target = one_week_ago - timedelta(days=(one_week_ago.weekday() - target_weekday) % 7)
                result["date"] = self.get_most_recent_trading_day(last_week_target)
                date_found = True

        if not date_found:
            date_match = re.search(r"\d{4}[-./]\d{1,2}[-./]\d{1,2}", text)
            if date_match:
                try:
                    normalized = date_match.group().replace(".", "-").replace("/", "-")
                    parsed = datetime.strptime(normalized, "%Y-%m-%d").date()
                    result["date"] = parsed.strftime("%Y-%m-%d")
                    date_found = True
                except ValueError:
                    pass

        # 2. 종목 추출
        if not is_screening:
            resolver = SymbolResolverAgent()
            context = await resolver.handle(context)
            result["symbol"] = context.get("symbol")
            symbol = context.get("symbol")
            
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

        if "RSI" in text.upper():
            rsi_match = re.search(r'RSI.*?(\d+)', text, re.IGNORECASE)
            if rsi_match:
                condition["rsi"] = f">{rsi_match.group(1)}"

        if "거래량" in text and any(word in text for word in ["줄어든", "감소", "하락", "낮은"]):
            condition["volume_direction"] = "down"
        elif "거래량" in text and any(word in text for word in ["늘어난", "증가", "상승", "급등"]):
            condition["volume_direction"] = "up"

        vol_change_match = re.search(r'거래량.*?(\d+)\s*%?', text)
        if vol_change_match:
            condition["volume_change"] = f"{vol_change_match.group(1)}%"

        result["condition"] = condition

        # 4. 개수 제한 추출
        limit_match = re.search(r"(\d+)\s*(개|종목)", text)
        if limit_match:
            result["limit"] = int(limit_match.group(1))

        # 5. 태스크 유형 설정
        result["task"] = "screening" if is_screening else "simple_inquiry"

        if is_screening and "symbol" in result:
            del result["symbol"]

        # 6. 결과를 context에 기록
        context["intent"] = result
        return result

    def _is_screening_intent(self, text: str) -> bool:
        screening_patterns = ["이상", "미만", "상위", "하위", "증가", "급등", "종목", "퍼센트", "비율", "전날 대비", "조건", "검색"]
        return any(kw in text for kw in screening_patterns)