from tools.market_data_tools import get_price, get_top_volume_stocks
from .base_agent import BaseAgent

class MarketDataAgent(BaseAgent):
    def process(self, params):
        if params['type'] == 'price':
            return get_price(params['ticker'])
        elif params['type'] == 'top_volume':
            return get_top_volume_stocks(params.get('n', 10))
        else:
            return "지원하지 않는 MarketData 요청입니다."