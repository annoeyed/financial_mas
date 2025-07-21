class MemoryManager:
    def __init__(self):
        self.memory = []

    def add(self, query, result):
        self.memory.append({'query': query, 'result': result})

    def get_all(self):
        return self.memory