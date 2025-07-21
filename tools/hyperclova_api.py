# tools/hyperclova_api.py

import requests

def analyze_intent_with_hyperclova(query):
    # 실제 API 엔드포인트, 인증키 등은 본인 환경에 맞게 수정
    url = "https://clova-api-url/your-endpoint"
    headers = {
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": query,
        "max_tokens": 32,
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['result']
    else:
        return "HyperCLOVA API 호출 실패"