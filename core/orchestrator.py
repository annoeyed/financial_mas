import asyncio
import yaml
from agents.market_data_agent import MarketDataAgent
from agents.technical_agent import TechnicalAgent
from agents.screening_agent import ScreeningAgent
from agents.signal_agent import SignalAgent
from agents.intent_agent import IntentAgent
from utils.logger import logger

class FinancialOrchestrator:
    def __init__(self, config_path="config/agents.yaml"):
        cfg = yaml.safe_load(open(config_path, "r"))
        # 인스턴스 생성
        self.agents = {
            "market_data_agent": MarketDataAgent(),
            "technical_agent": TechnicalAgent(),
            "screening_agent": ScreeningAgent(),
            "signal_agent": SignalAgent(),
            "intent_agent": IntentAgent()
        }
        # (추가) task_classifier, memory_manager 등 필요 모듈 로드

    async def process_query(self, query: str) -> dict:
        # 1) 의도 분류
        task_type = await self.agents["intent_agent"].process(query)
        task = task_type["intent"]

        # 2) 에이전트 매핑
        mapping = {
            "stock_recommendation": ["market_data_agent", "technical_agent"],
            "screening": ["screening_agent", "market_data_agent"],
            "signal_detection": ["signal_agent", "technical_agent"],
            "intent_clarification": ["intent_agent"]
        }
        selected = mapping.get(task, ["market_data_agent"])

        # 3) 병렬 실행
        tasks = [self.agents[name].process(query) for name in selected]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 4) 예외 필터링 & 통합
        final = []
        for res in results:
            if isinstance(res, Exception):
                logger.error(f"Agent 오류: {res}")
            else:
                final.append(res)
        return {"task": task, "results": final}
