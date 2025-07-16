import asyncio
from utils.logger import logger

class BaseAgent:
    def __init__(self, name: str):
        self.name = name

    async def process(self, query: str) -> dict:
        """각 Agent가 구현해야 할 진입점."""
        raise NotImplementedError

    async def call_api(self, fn, *args, retries: int = 2):
        """공통 API 호출 + 재시도 로직."""
        for i in range(retries + 1):
            try:
                return await fn(*args)
            except Exception as e:
                logger.warning(f"{self.name} API 호출 실패({i}/{retries}): {e}")
                await asyncio.sleep(0.5)
        raise RuntimeError(f"{self.name} 최대 재시도 실패")
