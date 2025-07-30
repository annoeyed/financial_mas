from agents.base_agent import BaseAgent
from utils.symbol_resolver import extract_symbol
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

    def handle(self, text: str) -> dict:
        if not isinstance(text, str):
            raise TypeError(f"[QueryUnderstanderAgent] handle() expects a string, got {type(text)}")

        result = {}
        text = text.strip()

        # 0. intent 분기
        is_screening = self._is_screening_intent(text)

        # 1. 날짜 추출
        date_keywords = {"오늘": 0, "어제": 1, "그저께": 2, "3일 전": 3, "4일 전": 4, "5일 전": 5, "6일 전": 6, "일주일 전": 7}

        weekday_map = {"월요일": 0, "화요일": 1, "수요일": 2, "목요일": 3, "금요일": 4, "토요일": 5, "일요일": 6}

        date_found = False

        # 상대 날짜 키워드 처리
        for keyword, days_ago in date_keywords.items():
            if keyword in text:
                ref = datetime.today() - timedelta(days=days_ago)
                result["date"] = self.get_most_recent_trading_day(ref)
                date_found = True
                break

        # 두 날짜 비교 (예: 어제 거래량이 그저께보다 줄어든 종목)
        if "어제" in text and "그저께" in text:
            to_date = self.get_most_recent_trading_day(datetime.today() - timedelta(days=1))  # 어제
            from_date = self.get_most_recent_trading_day(datetime.today() - timedelta(days=2))  # 그저께
            result["date_range"] = {"from": from_date, "to": to_date}
            date_found = True

        # "지난주 화요일" 등 요일 기반 표현 처리
        if not date_found:
            match = re.search(r"지난주\s*(월요일|화요일|수요일|목요일|금요일|토요일|일요일)", text)
            if match:
                target_weekday_str = match.group(1)
                target_weekday = weekday_map[target_weekday_str]
                today = datetime.today()
                one_week_ago = today - timedelta(days=7)
                last_week_target = one_week_ago - timedelta(days=(one_week_ago.weekday() - target_weekday) % 7)
                result["date"] = self.get_most_recent_trading_day(last_week_target)
                date_found = True

        # yyyy-mm-dd 직접 지정된 날짜 패턴
        if not date_found:
            date_match = re.search(r"\d{4}[-./]\d{1,2}[-./]\d{1,2}", text)
            if date_match:
                try:
                    normalized = date_match.group().replace(".", "-").replace("/", "-")
                    parsed_date = datetime.strptime(normalized, "%Y-%m-%d").date()
                    result["date"] = parsed_date.strftime("%Y-%m-%d")
                    date_found = True
                except ValueError as ve:
                    print(f"[DEBUG] 날짜 파싱 실패: {ve}")

        if not date_found:
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
        if "거래량" in text and any(word in text for word in ["줄어든", "감소", "하락", "감소한", "낮은"]):
            condition["volume_direction"] = "down"
        elif "거래량" in text and any(word in text for word in ["늘어난", "증가", "상승", "급등"]):
            condition["volume_direction"] = "up"

        # 거래량 변화 수치 조건 추출 (예: 3% 이상 감소한 종목)
        vol_change_match = re.search(r'거래량.*?(\d+)\s*%?', text)
        if vol_change_match:
            condition["volume_change"] = f"{vol_change_match.group(1)}%"


        result["condition"] = condition

        # 4. 개수 제한 추출
        limit_match = re.search(r"(\d+)\s*(개|종목)", text)
        if limit_match:
            result["limit"] = int(limit_match.group(1))
  
        if is_screening and "symbol" in result:
            del result["symbol"]
        
        return result

    def _is_screening_intent(self, text: str) -> bool:
        """
        symbol이 명시되지 않고 '조건'이나 '스캔' 같은 표현이 있을 경우 스크리닝으로 판단.
        """
        screening_patterns = ["이상", "미만", "상위", "하위", "증가", "급등", "종목", "퍼센트", "비율", "전날 대비", "조건", "검색"]
        return any(kw in text for kw in screening_patterns)