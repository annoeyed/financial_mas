import time
from utils.logger import logger

class BaseAgent:
    def __init__(self, name: str):
        self.name = name

    def process(self, query: dict) -> dict:
        """
        각 Agent가 반드시 구현해야 하는 핵심 메서드.
        예: structured dict → 결과 dict
        """
        raise NotImplementedError(f"{self.name} 에이전트는 process()를 구현해야 합니다.")

    def call_api(self, fn, *args, retries: int = 2, delay: float = 0.5):
        """
        공통 API 호출 유틸 (재시도 포함).
        :param fn: 호출할 함수
        :param args: 함수 인자들
        :param retries: 최대 재시도 횟수
        :param delay: 실패 시 대기 시간 (초)
        """
        for attempt in range(retries + 1):
            try:
                return fn(*args)
            except Exception as e:
                logger.warning(f"[{self.name}] API 호출 실패 ({attempt + 1}/{retries}): {e}")
                time.sleep(delay)

        raise RuntimeError(f"[{self.name}] 최대 재시도 실패 - API 호출 불가")