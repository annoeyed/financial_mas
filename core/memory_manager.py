# core/memory_manager.py

class MemoryManager:
    """대화 세션 및 상태 관리"""
    def __init__(self):
        self.sessions = {}

    def get(self, session_id: str) -> dict:
        return self.sessions.get(session_id, {})

    def update(self, session_id: str, data: dict):
        self.sessions[session_id] = {**self.sessions.get(session_id, {}), **data}