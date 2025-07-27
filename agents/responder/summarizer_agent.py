from agents.base_agent import BaseAgent
from api.hyperclova_api import generate_answer

class SummarizerAgent(BaseAgent):
    def __init__(self):
        super().__init__("SummarizerAgent")

    def handle(self, context: dict) -> dict:
        user_query = context.get("query")
        judgment = context.get("judgment", {})

        if not isinstance(judgment, dict):
            return {
                "response": "판단 결과가 유효하지 않아 응답을 생성할 수 없습니다.",
                "raw": context
            }

        judgment_type = judgment.get("judgment_type")

        # Screening 판단 결과 요약이 있을 경우, 해당 요약을 그대로 사용
        if judgment_type == "screening" and "judgment_summary" in judgment:
            explanation = judgment["judgment_summary"]
        else:
            explanation = judgment.get("explanation") or self.format_judgment(judgment)

        prompt = f"""다음은 사용자의 질문과 판단된 정답입니다.

    질문: {user_query}

    판단 결과: {explanation}

    위 내용을 사용자에게 금융 전문가처럼 정중하고 간결하게 설명해주세요."""

        answer = generate_answer(prompt)

        return {
            "response": answer,
            "raw": {
                "query": user_query,
                "structured": context.get("structured"),
                "judgment": judgment
            }
        }


    def explain_with_doc(self, judgment, data_pool) -> dict:
        """
        fallback 상황에서 RAG 문서 기반 보완 설명 생성
        """
        keyword = data_pool.get_metadata("keyword") or "관련 키워드"
        doc = data_pool.get_doc_section(keyword) or "관련 문서를 찾을 수 없습니다."

        prompt = f"""사용자의 질문에 대해 판단이 불완전하였으며,
관련 문서에서 보조 정보를 찾았습니다.

질문: {judgment.get('query', '[질문 없음]')}

문서 발췌:
{doc}

이 문서를 기반으로, 사용자의 질문에 대한 정보를 요약 정리해 금융 전문가처럼 응답해주세요."""

        answer = generate_answer(prompt)

        return {
            "response": answer,
            "raw": {
                "judgment": judgment,
                "doc": doc
            }
        }

    def format_judgment(self, judgment: dict) -> str:
        """
        judgment dict를 사람이 읽을 수 있는 형태로 정리 (fallback용 보조 함수)
        """
        if "price" in judgment:
            return f"시가는 {judgment['price']}원입니다."
        elif "rsi" in judgment:
            return f"RSI는 {judgment['rsi']}입니다."
        elif "change_ratio" in judgment:
            return f"거래량 변화율은 {judgment['change_ratio']}%입니다."
        else:
            return "판단 결과 상세 정보가 부족합니다."