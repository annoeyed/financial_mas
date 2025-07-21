from .intent_agent import IntentAgent
from .market_data_agent import MarketDataAgent
from .screening_agent import ScreeningAgent
from .signal_agent import SignalAgent
from .meaning_agent import MeaningAgent
from .special_agent import SpecialAgent

class Orchestrator:
    def __init__(self):
        self.intent_agent = IntentAgent()
        self.market_data_agent = MarketDataAgent()
        self.screening_agent = ScreeningAgent()
        self.signal_agent = SignalAgent()
        self.meaning_agent = MeaningAgent()
        self.special_agent = SpecialAgent()

    def handle_query(self, query):
        task_type, params = self.intent_agent.analyze(query)
        if task_type == "market_data":
            return self.market_data_agent.process(params)
        elif task_type == "screening":
            return self.screening_agent.process(params)
        elif task_type == "signal":
            return self.signal_agent.process(params)
        elif task_type == "meaning":
            return self.meaning_agent.process(params)
        elif task_type == "special":
            return self.special_agent.process(params)
        else:
            return "지원하지 않는 질의입니다."