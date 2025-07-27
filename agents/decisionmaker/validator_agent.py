from agents.base_agent import BaseAgent
from api.hyperclova_api import generate_answer

class ValidatorAgent(BaseAgent):
    def __init__(self):
        super().__init__("ValidatorAgent")

    def handle(self, query: str, structured: dict) -> dict:
        """
        질문이 유효한지 판단하고, 필요한 정보를 모두 포함하고 있는지 확인함
        """
        intent = structured.get("intent", "")
        entities = structured.get("entities", {})

        prompt = f"""
        다음 질문은 사용자가 입력한 금융 관련 질의입니다:
        "{query}"

        이 질문은 다음과 같이 구조화되었습니다:
        intent: {intent}
        entities: {entities}

        이 질문이 의도(intent) 파악과 정보 추출에 충분한 정보를 제공하는지 '예' 또는 '아니오'로 대답하고,
        부족하다면 어떤 정보가 부족한지 명시하세요.
        """

        validation = generate_answer(prompt)
        return {"validation": validation.strip()}