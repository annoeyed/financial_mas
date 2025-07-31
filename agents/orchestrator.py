import asyncio
import yaml
from datetime import datetime
from agents.interpreter.query_understander_agent import QueryUnderstanderAgent
from agents.decisionmaker.advanced_agent import AdvancedAgent
from agents.decisionmaker.ambiguous_agent import AmbiguousAgent
from agents.decisionmaker.analyzer_agent import AnalyzerAgent
from agents.decisionmaker.screener_agent import ScreeningAgent
from agents.decisionmaker.signal_agent import SignalAgent
from agents.responder.summarizer_agent import SummarizerAgent
from utils.logger import logger


class Orchestrator:
    def __init__(self, config_path="config/agents.yaml"):

        self.agents = {
            "query_understander": QueryUnderstanderAgent(),
            "ambiguous": AmbiguousAgent(),
            "analyzer": AnalyzerAgent(),
            "screener": ScreeningAgent(),
            "signal": SignalAgent(),
            "advanced": AdvancedAgent(),
            "summarizer": SummarizerAgent()
        }

        self.pipeline = [
            "query_understander",  # 의도 분석 → context 생성
            "ambiguous",           # 모호성 판단
            "analyzer",            # 수치 기반 단순 정답 도출
            "screener",            # 조건 기반 필터링
            "signal",              # 기술적 신호 감지
            "advanced",            # 특화 기능 처리
            "summarizer"           # 자연어 응답 생성
        ]

    async def async_run(self, query: str) -> dict:
        context = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "intent": {},
            "results": {},
            "logs": [],
            "clarification_needed": False
        }

        try:
            for agent_name in self.pipeline:
                agent = self.agents[agent_name]
                logger.debug(f"[Orchestrator] {agent_name} 실행 시작")

                try:
                    output = await agent.process(context)
                    if output:
                        context["results"][agent_name] = output
                        
                        # 특정 에이전트의 결과를 context에 직접 저장
                        if agent_name == "analyzer" and output.get("judgment"):
                            context["judgment"] = output.get("judgment")
                        elif agent_name == "screener" and output.get("judgment"):
                            context["judgment"] = output.get("judgment")
                        elif agent_name == "signal" and output.get("judgment"):
                            context["judgment"] = output.get("judgment")
                        elif agent_name == "advanced" and output.get("judgment"):
                            context["judgment"] = output.get("judgment")

                    if agent_name == "ambiguous" and output.get("clarification_needed"):
                        context["clarification_needed"] = True
                        context["response"] = output.get("message", "질문을 명확히 해주세요.")
                        break

                except Exception as e:
                    logger.warning(f"[Orchestrator] {agent_name} 실행 실패: {e}")
                    context["logs"].append({
                        "agent": agent_name,
                        "error": str(e)
                    })

            if context.get("clarification_needed"):
                return {
                    "clarification_needed": True,
                    "response": context["response"]
                }

            # summarizer의 응답 구조에 맞게 수정
            summarizer_result = context["results"].get("summarizer", {})
            if isinstance(summarizer_result, dict):
                response = summarizer_result.get("response", "응답 없음")
            else:
                response = str(summarizer_result) if summarizer_result else "응답 없음"
                
            return {
                "response": response,
                "intent": context["intent"],
                "intermediate": context["results"]
            }

        except Exception as e:
            logger.error(f"[Orchestrator] 전체 파이프라인 실패: {e}")
            return {"error": str(e), "query": query}

    def run(self, query: str):
        return asyncio.run(self.async_run(query))