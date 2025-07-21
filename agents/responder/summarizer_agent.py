from agents.base_agent import BaseAgent
from utils.hyperclova_api import generate_answer

class SummarizerAgent(BaseAgent):
    def __init__(self):
        super().__init__("SummarizerAgent")

    def process(self, summary_input: dict) -> dict:
        """
        summary_input 예시:
        {
            "query": "최근 많이 오른 주식 알려줘",
            "structured": {
                "intent": "vague_request",
                "target": "삼성전자",
                "condition": "상승률 기준 필요",
                "date": "최근",
                "is_ambiguous": true
            },
            "result": {
                "rise_rate": 21.43,
                "judgement": True
            }
        }
        """

        prompt = self.build_prompt(summary_input)

        answer = self.call_api(generate_answer, prompt)

        return {"final_answer": answer}

    def build_prompt(self, summary_input: dict) -> str:
        query = summary_input.get("query")
        structured = summary_input.get("structured", {})
        result = summary_input.get("result", {})

        # 간단한 예시 프롬프트
        return f"""
당신은 친절한 금융 AI 비서입니다.

[사용자 질문]
{query}

[의도 분석 결과]
- 의도: {structured.get('intent')}
- 대상: {structured.get('target')}
- 조건: {structured.get('condition')}
- 날짜: {structured.get('date')}
- 모호성 있음?: {structured.get('is_ambiguous')}

[판단 결과]
{result}

위의 정보를 바탕으로 사용자에게 자연스러운 문장으로 답변해주세요.
숫자는 요약하되, 설명은 구체적으로 해주세요.
"""