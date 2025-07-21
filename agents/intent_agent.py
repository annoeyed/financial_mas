from .base_agent import BaseAgent
from tools.hyperclova_api import analyze_intent_with_hyperclova

class IntentAgent(BaseAgent):
    def analyze(self, query):
        # HyperCLOVA로 의도 분석 (실제론 더 복잡하게 구현)
        intent = analyze_intent_with_hyperclova(query)
        # 아래는 단순 키워드 매칭 예시
        if "상위" in query and "거래량" in query:
            return "market_data", {"type": "top_volume", "n": 10}
        elif "이동평균" in query or "돌파" in query:
            return "signal", {"ma_days": 50, "percent": 10}
        elif "%" in query and "거래량" in query:
            return "screening", {"percent": 10}
        elif "가격" in query or "종가" in query:
            return "market_data", {"type": "price", "ticker": "AAPL"}
        elif "많이 오른" in query:
            return "meaning", {"type": "rising", "n": 5}
        elif "많이 떨어진" in query:
            return "meaning", {"type": "falling", "n": 5}
        elif "특화" in query or "알림" in query:
            return "special", {}
        else:
            return "unknown", {}