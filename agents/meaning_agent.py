from tools.market_data_tools import get_top_rising_stocks, get_top_falling_stocks
from .base_agent import BaseAgent

class MeaningAgent(BaseAgent):
    def process(self, params):
        if params['type'] == 'rising':
            return get_top_rising_stocks(params.get('n', 5))
        elif params['type'] == 'falling':
            return get_top_falling_stocks(params.get('n', 5))
        else:
            return "지원하지 않는 의미 해석 요청입니다."