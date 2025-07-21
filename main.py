from agents.orchestrator import Orchestrator

def main():
    orchestrator = Orchestrator()
    while True:
        query = input("질문을 입력하세요: ")
        if query == "exit":
            break
        result = orchestrator.handle_query(query)
        print("결과:", result)

if __name__ == "__main__":
    main()