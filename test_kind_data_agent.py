from agents.datagatherer.kind_data_agent import KINDDataAgent

def test_kind():
    agent = KINDDataAgent()
    structured = {"target": "삼성전자"}  # 예시 기업명
    result = agent.process(structured)
    print("결과:", result)

if __name__ == "__main__":
    test_kind()
