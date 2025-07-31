import asyncio
import time
import random
from datetime import datetime, timedelta
from agents.base_agent import BaseAgent
from utils.cache_manager import CacheManager
import yfinance as yf


class AmbiguousAgent(BaseAgent):
    def __init__(self, test_mode=False):
        super().__init__("AmbiguousAgent")
        self.cache_manager = CacheManager()
        self.test_mode = test_mode

    async def handle(self, context: dict) -> dict:
        # query_understander의 결과를 확인
        intent = context.get("intent", {})
        query = context.get("query", "")
        
        # 기본적인 주가 조회나 종목 정보 요청은 모호하지 않음
        if intent.get("task") == "simple_inquiry" and intent.get("symbol"):
            return {
                "clarification_needed": False,
                "message": "질문이 명확합니다."
            }
        
        # 스크리닝 요청도 모호하지 않음
        if intent.get("task") == "screening":
            return {
                "clarification_needed": False,
                "message": "스크리닝 요청이 명확합니다."
            }
        
        # 특별한 패턴이 있는 경우만 모호함으로 판단
        ambiguous_patterns = [
            "어떤", "무엇", "어떻게", "어디", "언제", "누가",
            "추천", "좋은", "나쁜", "최고", "최악",
            "어떤 종류", "무슨 종목", "어떤 주식"
        ]
        
        is_ambiguous = any(pattern in query for pattern in ambiguous_patterns)
        
        if is_ambiguous:
            return {
                "clarification_needed": True,
                "response": "어떤 종류의 주식을 찾으시나요?",
                "clarification": {
                    "message": "예시를 선택하거나 기준을 명확히 입력해주세요.",
                    "options": [
                        {"label": "최근 많이 오른 주식", "value": "recent_rise"},
                        {"label": "고점 대비 많이 떨어진 주식", "value": "peak_drop"}
                    ]
                }
            }
        else:
            return {
                "clarification_needed": False,
                "message": "질문이 명확합니다."
            }

    async def _handle_recent_rise(self, query: dict) -> dict:
        days = query.get("days", 10)
        threshold = query.get("threshold", 10)
        limit = query.get("limit", 10)

        symbols = self._get_filtered_symbols()

        results = []
        for symbol in symbols:
            perf = self._calculate_recent_performance(symbol, days)
            if perf and perf["performance"] >= threshold:
                results.append(perf)

        results.sort(key=lambda x: x["performance"], reverse=True)

        return {
            "clarification_needed": False,
            "success": True,
            "type": "recent_rise",
            "criteria": f"최근 {days}일간 {threshold}% 이상 상승",
            "user_message": f"최근 {days}일간 {threshold}% 이상 오른 종목 {len(results)}개",
            "stocks": results[:limit],
            "total_found": len(results)
        }

    async def _handle_peak_drop(self, query: dict) -> dict:
        days = query.get("days", 252)
        threshold = query.get("threshold", -20)
        limit = query.get("limit", 10)

        symbols = self._get_filtered_symbols()

        results = []
        for symbol in symbols:
            drop = self._calculate_peak_drop(symbol, days)
            if drop and drop["drop_ratio"] <= threshold:
                results.append(drop)

        results.sort(key=lambda x: x["drop_ratio"])

        return {
            "clarification_needed": False,
            "success": True,
            "type": "peak_drop",
            "criteria": f"최근 {days}일간 고점 대비 {abs(threshold)}% 이상 하락",
            "user_message": f"52주 고점 대비 {abs(threshold)}% 이상 하락한 종목 {len(results)}개",
            "stocks": results[:limit],
            "total_found": len(results)
        }

    def _get_filtered_symbols(self, limit_symbols=20):
        stable = [
            "005930", "000660", "035420", "051910", "006400", "035720", "207940",
            "068270", "323410", "051900", "006380", "017670", "015760", "028260",
            "032830", "086790", "055550", "105560", "139480", "024110"
        ]
        return [f"{code}.KS" for code in stable][:limit_symbols]

    def _calculate_recent_performance(self, symbol: str, days: int = 10):
        try:
            cache_key = f"recent_perf_{symbol}_{days}"
            cached = self.cache_manager.get("recent_performance", symbol, str(days))
            if cached:
                return cached

            if not self.test_mode:
                time.sleep(random.uniform(0.1, 0.3))

            end = datetime.today().date()
            start = end - timedelta(days=days + 10)
            df = yf.download(symbol, start=start, end=end, progress=False)

            if df.empty or len(df) < 2:
                return None

            recent = df["Close"].iloc[-1]
            past = df["Close"].iloc[-min(days, len(df) - 1)]
            perf = ((recent - past) / past) * 100

            result = {
                "symbol": symbol,
                "recent_price": round(float(recent), 2),
                "past_price": round(float(past), 2),
                "performance": round(perf, 2),
                "days": days
            }

            self.cache_manager.set("recent_performance", symbol, str(days), result)
            return result
        except:
            return None

    def _calculate_peak_drop(self, symbol: str, days: int = 252):
        try:
            cache_key = f"peak_drop_{symbol}_{days}"
            cached = self.cache_manager.get("peak_drop", symbol, str(days))
            if cached:
                return cached

            if not self.test_mode:
                time.sleep(random.uniform(0.1, 0.3))

            end = datetime.today().date()
            start = end - timedelta(days=days + 30)
            df = yf.download(symbol, start=start, end=end, progress=False)

            if df.empty or len(df) < 10:
                return None

            peak = df["High"].max()
            curr = df["Close"].iloc[-1]
            drop = ((curr - peak) / peak) * 100

            result = {
                "symbol": symbol,
                "current_price": round(float(curr), 2),
                "peak_price": round(float(peak), 2),
                "drop_ratio": round(drop, 2),
                "days": days
            }

            self.cache_manager.set("peak_drop", symbol, str(days), result)
            return result
        except:
            return None