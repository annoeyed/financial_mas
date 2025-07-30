import asyncio
from abc import ABC, abstractmethod
from utils.logger import logger

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.state = {}

    async def process(self, context: dict) -> dict:
        """
        Orchestrator가 호출하는 메인 진입점.
        각 agent는 context를 읽고, 필요한 작업을 수행해 dict를 반환.
        """
        try:
            result = await self.handle(context)
            return result or {}
        except Exception as e:
            logger.error(f"[{self.name}] 처리 중 예외 발생: {e}")
            raise

    @abstractmethod
    async def handle(self, context: dict) -> dict:
        """
        실제 에이전트의 주요 작업을 구현해야 함.
        context에는 'query', 'intent', 'results' 등이 담겨 있음.
        """
        raise NotImplementedError(f"[{self.name}] handle()을 구현해야 합니다.")

    def update_state(self, key, value):
        """에이전트 내부 상태 기록"""
        self.state[key] = value

    def get_state(self, key, default=None):
        return self.state.get(key, default)

    async def call_api(self, fn, *args, retries: int = 2, delay: float = 0.5):
        """
        공통 API 호출 유틸 (비동기 지원, 재시도 포함).
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
                await asyncio.sleep(delay)

        logger.error(f"[{self.name}] 최대 재시도 실패 - API 호출 불가")
        raise RuntimeError(f"[{self.name}] API 호출 실패")