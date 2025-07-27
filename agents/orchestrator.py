from agents.interpreter.query_understander_agent import QueryUnderstanderAgent
from agents.interpreter.ambiguity_resolver_agent import AmbiguityResolverAgent
from agents.dataprovider.data_provider_agent import DataProviderAgent
from agents.decisionmaker.analyzer_agent import AnalyzerAgent
from agents.decisionmaker.validator_agent import ValidatorAgent
from agents.decisionmaker.screener_agent import ScreeningAgent
from agents.responder.summarizer_agent import SummarizerAgent
from datapool.data_pool import DataPool

class Orchestrator:
    def __init__(self):
        self.query_understander = QueryUnderstanderAgent()
        self.ambiguity_resolver = AmbiguityResolverAgent()
        self.data_provider = DataProviderAgent()
        self.analyzer = AnalyzerAgent()
        self.validator = ValidatorAgent()
        self.summarizer = SummarizerAgent()
        self.screener = ScreeningAgent()

    def run(self, raw_query: str) -> dict:
        try:
            parsed_query = self.query_understander.handle(raw_query)
            assert isinstance(parsed_query, dict), f"raw_query는 str이어야 합니다. 현재 타입: {type(raw_query)}"

            parsed_query["query"]=raw_query
            clarified_query = self.ambiguity_resolver.handle(parsed_query)
        
            if not isinstance(clarified_query, dict):
                raise TypeError(f"clarified_query는 dict여야 합니다. 현재 타입: {type(clarified_query)} / 값: {clarified_query}")


            if (
                clarified_query.get("symbol", {}).get("raw") is None
                and "condition" in clarified_query
                and clarified_query["condition"].get("volume_change")
            ):
                judgment = self.screener.handle(clarified_query)
          
                response = self.summarizer.handle({
                    "query": raw_query,
                    "structured": clarified_query,
                    "judgment": judgment,
                    "data_pool": None
                })
                return response

            data_pool = DataPool()
            self.data_provider.handle(clarified_query, data_pool)

            # 4. 판단 (정답 도출)
            judgment = self.analyzer.handle(clarified_query, data_pool)

            # 5. 응답 생성
            response = self.summarizer.handle({
                "query": raw_query,
                "structured": clarified_query,
                "judgment": judgment,
                "data_pool": data_pool
            })

            return response

        except Exception as e:
            return {
                "error": f"[Orchestrator] 실행 중 오류 발생: {str(e)}",
                "raw": {"error": str(e), "query": raw_query}
            }