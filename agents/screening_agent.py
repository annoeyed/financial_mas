from tools.market_data_tools import get_stocks_by_condition
from .base_agent import BaseAgent

class ScreeningAgent(BaseAgent):
    def process(self, params):
        percent = params.get('percent', 10)
        return get_stocks_by_condition(percent)