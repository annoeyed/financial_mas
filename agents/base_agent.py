import time
from abc import ABC, abstractmethod
from utils.logger import logger

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.state = {}

    @abstractmethod
    def handle(self, query: dict, **kwargs) -> dict:
        """
        에이전트가 반드시 구현해야 하는 메인 메서드.
        query는 해석된 구조화 입력. kwargs에는 DataPool 등 컨텍스트가 담김.
        """
        raise NotImplementedError(f"[{self.name}] handle()을 구현해야 합니다.")

    def update_state(self, key, value):
        """
        에이전트 내부 상태 기록 (예: confidence, fallback 요구 등).
        """
        self.state[key] = value

    def get_state(self, key, default=None):
        return self.state.get(key, default)

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

        logger.error(f"[{self.name}] 최대 재시도 실패 - API 호출 불가")
        raise RuntimeError(f"[{self.name}] API 호출 실패")