from .base_agent import BaseAgent
from tools.analysis_tools import compute_indicators

class TechnicalAgent(BaseAgent):
    def __init__(self):
        super().__init__("TechnicalAgent")

    async def process(self, query: str) -> dict:
        # MarketDataAgent 결과를 가져와야 실제로 쓰겠지만, 여기서는 간단히…
        params = {"query": query}
        indicators = await self.call_api(compute_indicators, params)
        return {"agent": self.name, "indicators": indicators}
