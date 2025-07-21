from tools.market_data_tools import get_signal_stocks
from .base_agent import BaseAgent

class SignalAgent(BaseAgent):
    def process(self, params):
        ma_days = params.get('ma_days', 50)
        percent = params.get('percent', 10)
        return get_signal_stocks(ma_days, percent)