from agents.orchestrator import Orchestrator

def main():
    print("금융 멀티에이전트 시스템 시작")

    orchestrator = Orchestrator()

    while True:
        query = input("\n사용자 질문: ").strip()
        if query.lower() in ["exit", "quit"]:
            print("시스템 종료")
            break

        result = orchestrator.run(query)

        print("\n응답 결과:")
        print(result)

if __name__ == "__main__":
    main()