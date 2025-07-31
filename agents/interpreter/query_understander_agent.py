from agents.base_agent import BaseAgent
from agents.interpreter.symbol_resolver_agent import SymbolResolverAgent
from dateutil.relativedelta import relativedelta
import re
from datetime import datetime, timedelta

# --- 상수 정의 ---
DATE_KEYWORDS = {"오늘": 0, "어제": 1, "그저께": 2, "3일 전": 3, "4일 전": 4, "5일 전": 5, "6일 전": 6, "일주일 전": 7}
WEEKDAY_MAP = {"월요일": 0, "화요일": 1, "수요일": 2, "목요일": 3, "금요일": 4, "토요일": 5, "일요일": 6}
SCREENING_PATTERNS = ["이상", "미만", "상위", "하위", "증가", "급등", "감소", "하락", "종목", "퍼센트", "비율", "전날 대비", "조건", "검색"]
VOLUME_UP_KEYWORDS = ["늘어난", "증가", "상승", "급등"]
VOLUME_DOWN_KEYWORDS = ["줄어든", "감소", "하락", "낮은"]

# --- 정규 표현식 컴파일 ---
RE_LAST_WEEK = re.compile(r"지난주\s*(월요일|화요일|수요일|목요일|금요일|토요일|일요일)")
RE_DATE_FORMAT = re.compile(r"\d{4}[-./]\d{1,2}[-./]\d{1,2}")
RE_RSI = re.compile(r'RSI.*?(\d+)', re.IGNORECASE)
RE_VOLUME_CHANGE = re.compile(r'거래량.*?(\d+)\s*%?')
RE_LIMIT = re.compile(r"(\d+)\s*(개|종목)")


class QueryUnderstanderAgent(BaseAgent):
    def __init__(self):
        super().__init__("QueryUnderstanderAgent")
        self._symbol_resolver = SymbolResolverAgent()

    async def handle(self, context: dict[str, any]) -> dict[str, any]:
        """쿼리를 분석하고 구조화된 의도를 추출하는 메인 핸들러"""
        text = context.get("query", "")
        if not isinstance(text, str):
            raise TypeError(f"[{self.name}] query must be a string, got {type(text)}")
        
        text = text.strip()

        # 1. 태스크 유형 결정 (의도 파악)
        task_type = self._determine_task_type(text)
        
        # 2. 핵심 정보 추출
        date_info = self._extract_date_info(text)
        conditions = self._extract_conditions(text)
        limit = self._extract_limit(text)
        
        # 3. 결과 구조화
        result = {
            "task": task_type,
            "condition": conditions,
            **date_info # date 또는 date_range를 결과에 병합
        }
        if limit:
            result["limit"] = limit

        # 4. 태스크 유형에 따라 추가 정보 추출 (종목)
        if task_type == "simple_inquiry":
            result["symbol"] = await self._extract_symbol_info(context)
        
        # 5. 컨텍스트 업데이트 및 결과 반환
        context["intent"] = result
        return result

    def _determine_task_type(self, text: str) -> str:
        """쿼리 텍스트를 기반으로 태스크 유형(스크리닝/단순조회)을 결정합니다."""
        return "screening" if any(kw in text for kw in SCREENING_PATTERNS) else "simple_inquiry"

    def _extract_date_info(self, text: str) -> dict[str, any]:
        """쿼리에서 날짜 또는 날짜 범위를 추출합니다."""
        # 기간 추출 우선 ("어제부터 그저께까지" 같은 표현)
        if "어제" in text and "그저께" in text:
            to_date = self._get_most_recent_trading_day(datetime.today() - timedelta(days=1))
            from_date = self._get_most_recent_trading_day(datetime.today() - timedelta(days=2))
            return {"date_range": {"from": from_date, "to": to_date}}

        # 상대 날짜 키워드
        for keyword, days_ago in DATE_KEYWORDS.items():
            if keyword in text:
                ref_date = datetime.today() - timedelta(days=days_ago)
                return {"date": self._get_most_recent_trading_day(ref_date)}
        
        # "지난주 O요일" 패턴
        match = RE_LAST_WEEK.search(text)
        if match:
            target_weekday = WEEKDAY_MAP[match.group(1)]
            one_week_ago = datetime.today() - timedelta(days=7)
            days_diff = (one_week_ago.weekday() - target_weekday + 7) % 7
            last_week_target = one_week_ago - timedelta(days=days_diff)
            return {"date": self._get_most_recent_trading_day(last_week_target)}

        # YYYY-MM-DD 형식
        date_match = RE_DATE_FORMAT.search(text)
        if date_match:
            try:
                normalized = date_match.group().replace(".", "-").replace("/", "-")
                parsed = datetime.strptime(normalized, "%Y-%m-%d").date()
                return {"date": parsed.strftime("%Y-%m-%d")}
            except ValueError:
                pass # 잘못된 형식은 무시

        # 추출 실패 시 빈 딕셔너리 반환
        return {}

    async def _extract_symbol_info(self, context: dict[str, any]) -> dict[str, str | None]:
        """SymbolResolverAgent를 사용하여 쿼리에서 종목 정보를 추출합니다."""
        resolved_context = await self._symbol_resolver.handle(context)
        symbol = resolved_context.get("symbol")
        
        if isinstance(symbol, dict):
            return symbol
        if isinstance(symbol, str):
            return {"raw": symbol, "koreainvestment_code": None, "yfinance_code": None}
        
        return {"raw": None, "error": "종목코드 매핑 실패"}

    def _extract_conditions(self, text: str) -> dict[str, str]:
        """쿼리에서 스크리닝 조건을 추출합니다."""
        conditions = {}
        
        # RSI 조건
        rsi_match = RE_RSI.search(text)
        if rsi_match:
            conditions["rsi"] = f">{rsi_match.group(1)}"
            
        # 거래량 방향
        if "거래량" in text:
            if any(word in text for word in VOLUME_UP_KEYWORDS):
                conditions["volume_direction"] = "up"
            elif any(word in text for word in VOLUME_DOWN_KEYWORDS):
                conditions["volume_direction"] = "down"

        # 거래량 변화율
        vol_change_match = RE_VOLUME_CHANGE.search(text)
        if vol_change_match:
            conditions["volume_change"] = f"{vol_change_match.group(1)}%"
            
        return conditions

    def _extract_limit(self, text: str) -> int | None:
        """쿼리에서 결과 개수 제한을 추출합니다."""
        limit_match = RE_LIMIT.search(text)
        if limit_match:
            return int(limit_match.group(1))
        return None

    def _get_most_recent_trading_day(self, reference: datetime = None) -> str:
        """주어진 날짜를 기준으로 가장 가까운 과거 영업일을 찾아 반환합니다."""
        if reference is None:
            reference = datetime.today()
        
        weekday = reference.weekday()
        if weekday == 5:  # 토요일 -> 금요일
            reference -= timedelta(days=1)
        elif weekday == 6:  # 일요일 -> 금요일
            reference -= timedelta(days=2)
            
        return reference.strftime("%Y-%m-%d")