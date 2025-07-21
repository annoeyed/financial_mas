import os
import json
import uuid
import requests
from dotenv import load_dotenv

load_dotenv()
CLOVA_API_KEY = os.getenv("CLOVA_API_KEY")
CLOVA_API_URL = "https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003"

def generate_answer(prompt: str) -> str:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CLOVA_API_KEY}",
        "X-NCP-CLOVASTUDIO-REQUEST-ID": str(uuid.uuid4())
    }

    body = {
        "messages": [
            {"role": "system", "content": "당신은 금융 정보를 분석하고 구조화하는 에이전트입니다."},
            {"role": "user", "content": prompt}
        ],
        "top_p": 0.8,
        "temperature": 0.2,
        "max_tokens": 800
    }

    try:
        res = requests.post(CLOVA_API_URL, headers=headers, data=json.dumps(body))
        print(f"[DEBUG] 응답코드: {res.status_code}")
        print(f"[DEBUG] 응답본문: {res.text}")
        res.raise_for_status()
        
        response_json = res.json()
        return response_json["result"]["message"]["content"]

    except Exception as e:
        print(f"API 호출 실패: {e}")
        return "API 호출 중 오류 발생"