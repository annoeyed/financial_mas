from agents.interpreter.query_understander_agent import QueryUnderstanderAgent
from agents.datagatherer.yfinance_data_agent import YFinanceDataAgent
from agents.datagatherer.dart_data_agent import DARTDataAgent
from agents.datagatherer.kind_data_agent import KINDDataAgent
from agents.decisionmaker.reasoner_agent import ReasonerAgent
from agents.responder.summarizer_agent import SummarizerAgent

class Orchestrator:
    def __init__(self):
        self.query_understander = QueryUnderstanderAgent()
        self.yfinance_agent = YFinanceDataAgent()
        self.dart_agent = DARTDataAgent()
        self.kind_agent = KINDDataAgent()
        self.reasoner = ReasonerAgent()
        self.summarizer = SummarizerAgent()

    def run(self, query: str) -> dict:
        try:
            # 1. 질문 해석
            structured = self.query_understander.process(query)
            intent = structured.get("intent")
            print("구조화된 해석 결과:", structured)

            # 2. 데이터 수집
            if intent == "realtime_price_lookup" or intent == "technical_signal" or intent == "vague_request":
                data = self.yfinance_agent.process(structured)
            elif intent == "disclosure_query":
                data = self.dart_agent.process(structured)
            elif intent == "product_info":
                data = self.kind_agent.process(structured)
            else:
                return {"error": "지원하지 않는 intent입니다.", "structured": structured}

            print("수집된 데이터:", data)

            # 3. 판단
            structured_input = {
                "intent": intent,
                "target": structured.get("target"),
                "condition": structured.get("condition"),
                "data": data.get("data") if isinstance(data, dict) else data
            }

            result = self.reasoner.process(structured_input)
            print("판단 결과:", result)

            # 4. 응답 생성
            summary_input = {
                "query": query,
                "structured": structured,
                "result": result
            }

            final = self.summarizer.process(summary_input)
            return final

        except Exception as e:
            return {
                "error": f"오케스트레이터 실행 중 오류 발생: {str(e)}",
                "query": query
            }