from .base_agent import BaseAgent
from core.communication import TaskClassifier

class IntentAgent(BaseAgent):
    def __init__(self):
        super().__init__("IntentAgent")
        self.classifier = TaskClassifier()

    async def process(self, query: str) -> dict:
        intent = await self.classifier.classify(query)
        return {"agent": self.name, "intent": intent}
