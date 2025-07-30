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

        # 1. screening의 경우 summary 바로 반환
        if judgment.get("judgment_type") == "screening" and "judgment_summary" in judgment:
            
            limit = context.get("structured", {}).get("limit", 10)
            top_names = [item["name"] for item in judgment.get("judgment", [])][:limit]
            name_list_str = "\n".join([f"{i+1}. {name}" for i, name in enumerate(top_names)])

            return {
                "response": f"{judgment['judgment_summary']}\n\n종목 목록:\n{name_list_str}",
                "raw": {
                    "query": user_query,
                    "structured": context.get("structured"),
                    "judgment": judgment
                }
            }

        # 2. 설명이 있는 경우 그대로 사용
        if "explanation" in judgment:
            return {
                "response": judgment["explanation"],
                "raw": {
                    "query": user_query,
                    "structured": context.get("structured"),
                    "judgment": judgment
                }
            }

        # 3. 간단한 포맷 대응 (가격, RSI 등)
        formatted = self.format_judgment(judgment)
        if formatted:
            return {
                "response": formatted,
                "raw": {
                    "query": user_query,
                    "structured": context.get("structured"),
                    "judgment": judgment
                }
            }

        # 4. fallback: HyperCLOVA 호출
        prompt = f"""다음은 사용자의 질문과 판단된 정답입니다.

질문: {user_query}

판단 결과: {judgment}

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

    def format_judgment(self, judgment: dict) -> str:
        """
        judgment dict를 사람이 읽을 수 있는 형태로 정리
        """
        if "price" in judgment:
            return f"해당 종목의 현재 가격은 {judgment['price']}원입니다."
        elif "rsi" in judgment:
            return f"해당 종목의 RSI는 {judgment['rsi']}입니다."
        elif "change_ratio" in judgment:
            return f"거래량 변화율은 {judgment['change_ratio']}%입니다."
        return ""