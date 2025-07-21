from .base_agent import BaseAgent

class SpecialAgent(BaseAgent):
    def process(self, params):
        # 예시: 단순히 "특화 기능 실행됨" 반환
        return "특화 기능이 실행되었습니다! (예: 알림, 시각화 등)"