from agents.datagatherer.dart_data_agent import DARTDataAgent

from dotenv import load_dotenv

load_dotenv()

def test_dart_agent():
    agent = DARTDataAgent()
    structured = {"target": "삼성전자"}
    result = agent.process(structured)
    print("결과:", result)

if __name__ == "__main__":
    test_dart_agent()