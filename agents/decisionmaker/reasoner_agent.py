# agents/decisionmaker/reasoner_agent.py

from agents.base_agent import BaseAgent

class ReasonerAgent(BaseAgent):
    def __init__(self):
        super().__init__("ReasonerAgent")

    def process(self, structured_input: dict) -> dict:
        """
        structured_input 예시:
        {
            "intent": "technical_signal",
            "condition": "50일 이동평균선 상향 돌파",
            "target": "삼성전자",
            "data": {
                "close": 72000,
                "ma50": 65000
            }
        }
        """

        intent = structured_input.get("intent")
        condition = structured_input.get("condition")
        data = structured_input.get("data")
        target = structured_input.get("target")

        if not data:
            return {"error": "판단할 데이터가 없습니다."}

        if intent == "technical_signal":
            return self._handle_technical_signal(condition, data, target)

        elif intent == "vague_request":
            return self._handle_vague_condition(condition, data, target)

        elif intent == "screening":
            return self._handle_screening(condition, data)

        else:
            return {"message": "판단할 수 없는 intent입니다."}

    def _handle_technical_signal(self, condition, data, target):
        """
        예: 50일선 돌파 조건
        """
        if "이동평균" in condition:
            try:
                current = data["close"]
                moving_avg = data["ma50"]
                gap_ratio = (current - moving_avg) / moving_avg

                if gap_ratio >= 0.1:
                    return {
                        "signal": "상향 돌파",
                        "gap_ratio": round(gap_ratio * 100, 2),
                        "judgement": True,
                        "target": target
                    }
                else:
                    return {
                        "signal": "돌파 조건 미달",
                        "gap_ratio": round(gap_ratio * 100, 2),
                        "judgement": False,
                        "target": target
                    }
            except KeyError:
                return {"error": "기술적 분석에 필요한 값이 부족합니다."}

    def _handle_vague_condition(self, condition, data, target):
        """
        예: '많이 오른 종목' → 상승률 20% 이상
        """
        try:
            start_price = data["past_price"]
            current_price = data["close"]
            change = (current_price - start_price) / start_price

            judgement = change >= 0.2  # 예: 20% 이상 상승이면 true

            return {
                "target": target,
                "rise_rate": round(change * 100, 2),
                "judgement": judgement
            }
        except Exception:
            return {"error": "비교 기준 데이터 부족"}

    def _handle_screening(self, condition, data_list):
        """
        예: 필터링 조건 기반 랭킹 (복수 종목)
        data_list = [ {"ticker": "...", "volume": ..., "per": ..., ...}, ... ]
        """
        try:
            filtered = [
                d for d in data_list if d.get("volume", 0) > 1_000_000
            ]
            sorted_result = sorted(filtered, key=lambda d: d.get("volume", 0), reverse=True)

            return {
                "result": sorted_result[:10],
                "total_matched": len(sorted_result)
            }
        except Exception:
            return {"error": "screening 처리 중 오류 발생"}