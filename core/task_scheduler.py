# core/task_scheduler.py

import asyncio

class TaskScheduler:
    """주기 작업 스케줄러"""
    def __init__(self):
        self.tasks = []

    def schedule(self, coro, delay: float):
        async def wrapper():
            await asyncio.sleep(delay)
            return await coro()
        self.tasks.append(asyncio.create_task(wrapper()))

    async def shutdown(self):
        for t in self.tasks:
            t.cancel()