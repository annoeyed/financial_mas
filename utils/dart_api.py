# 실제 서비스에서는 get_corp_code()를 OpenDART의 corpCode.xml을 파싱하여 구현하거나 DB에 저장해 둬야 합니다.

import requests
import xml.etree.ElementTree as ET

DART_API_KEY = "YOUR_DART_API_KEY"

def get_corp_code(company_name: str) -> str:
    # 사전에 내려받은 corpCode.xml 파싱하거나 캐시 API 사용
    dummy_map = {
        "삼성전자": "00126380",
        "네이버": "00222046"
    }
    return dummy_map.get(company_name)

def fetch_financial_report(corp_code: str, year: str, field: str) -> str:
    """
    DART XBRL 공시 텍스트 기반으로 간단히 '영업이익' 등을 추출하는 예시
    """
    url = "https://opendart.fss.or.kr/api/fnlttSinglAcnt.json"
    params = {
        "crtfc_key": DART_API_KEY,
        "corp_code": corp_code,
        "bsns_year": year,
        "reprt_code": "11011",
        "fs_div": "CFS"
    }

    response = requests.get(url, params=params)
    json_data = response.json()

    if "list" not in json_data:
        return f"{year}년 재무제표 조회 실패"

    for item in json_data["list"]:
        if field in item.get("account_nm", ""):
            return item.get("thstrm_amount")

    return f"{field} 항목을 찾을 수 없음"