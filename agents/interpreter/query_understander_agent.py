from agents.base_agent import BaseAgent
from utils.hyperclova_api import generate_answer
import json

class QueryUnderstanderAgent(BaseAgent):
    def __init__(self):
        super().__init__("QueryUnderstanderAgent")

    def process(self, query: str) -> dict:
        """질문을 받아 intent, 구조화된 정보, 모호성 여부를 반환"""
        prompt = f"""
사용자의 질문을 아래 JSON 형식으로 분석해줘.

질문: \"{query}\"

형식:
{{
  "intent": "",  // 예: "realtime_price_lookup", "technical_signal", "vague_request", "disclosure_query"
  "target": "",  // 종목명 또는 대상
  "condition": "",  // 조건 또는 수치 기준 (있다면)
  "date": "",  // 날짜 (있다면)
  "is_ambiguous": true|false  // 모호한 표현이 포함되어 있는지 여부
}}
"""

        response = generate_answer(prompt)



        try:
            parsed = json.loads(response)
        except Exception as e:
            parsed = {
                "intent": "unknown",
                "target": None,
                "condition": None,
                "date": None,
                "is_ambiguous": True,
                "raw": response
            }


        return parsed