from agents.base_agent import BaseAgent
from api.hyperclova_api import generate_answer

class SummarizerAgent(BaseAgent):
    def __init__(self):
        super().__init__("SummarizerAgent")

    async def handle(self, context: dict) -> dict:
        user_query = context.get("query")
        judgment = context.get("judgment", {})
        structured = context.get("structured", {})

        # 1. 판단 결과가 없거나 비정상적인 경우 (validator 기능 대체)
        if not isinstance(judgment, dict) or not judgment:
            return {
                "response": "죄송합니다. 질문의 결과를 분석하는 데 필요한 정보가 충분하지 않습니다.",
                "raw": {
                    "query": user_query,
                    "structured": structured,
                    "judgment": judgment
                },
                "clarification_needed": True,
                "clarification": {
                    "message": "궁금하신 점을 조금 더 구체적으로 말씀해 주세요.",
                    "suggestions": [
                        "삼성전자 주가 알려줘",
                        "오늘 거래량이 급등한 종목은?",
                        "RSI가 70 이상인 종목 보여줘"
                    ]
                }
            }

        # 2. screening 타입은 judgment_summary와 name 목록 반환
        if judgment.get("judgment_type") == "screening" and "judgment_summary" in judgment:
            limit = structured.get("limit", 10)
            top_names = [item.get("name", "알 수 없음") for item in judgment.get("judgment", [])][:limit]
            name_list_str = "\n".join([f"{i+1}. {name}" for i, name in enumerate(top_names)])

            return {
                "response": f"{judgment['judgment_summary']}\n\n종목 목록:\n{name_list_str}",
                "raw": {
                    "query": user_query,
                    "structured": structured,
                    "judgment": judgment
                }
            }

        # 3. explanation이 있는 경우 직접 사용
        if "explanation" in judgment:
            return {
                "response": judgment["explanation"],
                "raw": {
                    "query": user_query,
                    "structured": structured,
                    "judgment": judgment
                }
            }

        # 4. 간단한 포맷에 대응
        formatted = self.format_judgment(judgment)
        if formatted:
            return {
                "response": formatted,
                "raw": {
                    "query": user_query,
                    "structured": structured,
                    "judgment": judgment
                }
            }

        # 5. fallback: HyperCLOVA-X 호출
        prompt = f"""다음은 사용자의 질문과 판단된 정답입니다.

질문: {user_query}

판단 결과: {judgment}

위 내용을 사용자에게 금융 전문가처럼 정중하고 간결하게 설명해주세요."""

        answer = generate_answer(prompt)

        return {
            "response": answer,
            "raw": {
                "query": user_query,
                "structured": structured,
                "judgment": judgment
            }
        }

    def format_judgment(self, judgment: dict) -> str:
        """
        judgment dict를 사람이 읽을 수 있는 형태로 정리
        """
        if "price" in judgment:
            price = judgment['price']
            if isinstance(price, (int, float)):
                return f"해당 종목의 현재 가격은 {price:,}원입니다."
            else:
                return f"해당 종목의 현재 가격은 {price}입니다."
        elif "rsi" in judgment:
            return f"해당 종목의 RSI는 {judgment['rsi']}입니다."
        elif "change_ratio" in judgment:
            return f"거래량 변화율은 {judgment['change_ratio']}%입니다."
        return ""