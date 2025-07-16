from .base_agent import BaseAgent
from tools.analysis_tools import screen_stocks

class ScreeningAgent(BaseAgent):
    def __init__(self):
        super().__init__("ScreeningAgent")

    async def process(self, query: str) -> dict:
        params = {"query": query}
        screened = await self.call_api(screen_stocks, params)
        return {"agent": self.name, "screened": screened}
