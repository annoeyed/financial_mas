from agents.orchestrator import Orchestrator

def run_fin_agent(query: str):
    orchestrator = Orchestrator()
    try:
        result = orchestrator.run(query)

        print("\n최종 응답:")
        if isinstance(result, dict):
            print(result.get("response") or result)
        else:
            print(result)
    except Exception as e:
        print(f"[오류 발생] {e}")

if __name__ == "__main__":
    print("금융 멀티에이전트 시스템에 오신 것을 환영합니다!")
    user_query = input("질문을 입력하세요: ").strip()

    if user_query:
        run_fin_agent(user_query)
    else:
        print("질문이 입력되지 않았습니다.")