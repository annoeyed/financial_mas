from agents.base_agent import BaseAgent
from api.hyperclova_api import generate_answer

class AmbiguityResolverAgent(BaseAgent):
    def __init__(self):
        super().__init__("AmbiguityResolverAgent")

    def handle(self, structured: dict) -> dict:
        # 방어: 타입 확인
        if not isinstance(structured, dict):
            raise TypeError(f"[AmbiguityResolverAgent] 입력이 dict가 아님: {type(structured)} → {structured}")

        query = structured.get("query", "")
        intent = structured.get("intent", "")

        prompt = f"""
        사용자가 질문한 문장은 다음과 같습니다:
        "{query}"

        이 문장이 너무 모호하거나 불분명할 경우, 추가로 어떤 정보를 물어봐야 명확해질까요?
        intent는 "{intent}" 입니다.
        명확성을 높이기 위한 follow-up 질문을 한 문장으로 제시하세요.
        """
        clarification = generate_answer(prompt)

        # 방어: generate_answer 실패 시
        if not isinstance(clarification, str):
            clarification = "명확한 질문으로 다시 입력해주세요."

        structured["clarification"] = clarification.strip()
        return structured