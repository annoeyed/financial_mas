import os
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from agents.base_agent import BaseAgent

CORPCODE_FILE = "CORPCODE.xml"

class DARTDataAgent(BaseAgent):
    def __init__(self):
        super().__init__("DARTDataAgent")
        self.dart_api_key = os.getenv("DART_API_KEY")
        self.corp_dict = self._load_corp_codes()

    def _load_corp_codes(self):
        """
        CORPCODE.xml 파일을 파싱해 {'회사명': 'corp_code'} 딕셔너리 반환
        """
        if not os.path.exists(CORPCODE_FILE):
            raise FileNotFoundError(f"{CORPCODE_FILE} 파일이 존재하지 않습니다. 먼저 다운로드하세요.")

        corp_dict = {}
        tree = ET.parse(CORPCODE_FILE)
        root = tree.getroot()

        for item in root.findall("list"):
            name = item.findtext("corp_name", "").strip()
            code = item.findtext("corp_code", "").strip()
            if name and code:
                corp_dict[name] = code

        return corp_dict

    def process(self, structured: dict) -> dict:
        """
        structured dict에서 'target'을 받아 회사명으로 corp_code 조회하고,
        해당 corp_code로 공시 목록 조회
        """
        target = structured.get("target", "").strip()
        if not target:
            return {"error": "대상 종목명이 없습니다."}

        corp_code = self.corp_dict.get(target)

        if not corp_code:
            similar = [name for name in self.corp_dict if target in name]
            if similar:
                matched = similar[0]
                corp_code = self.corp_dict[matched]
            else:
                return {"error": f"기업 이름 '{target}' 으로 corp_code를 찾을 수 없습니다."}

        url = "https://opendart.fss.or.kr/api/list.json"
        params = {
            "crtfc_key": self.dart_api_key,
            "corp_code": corp_code,
            "bgn_de": datetime.now().strftime("%Y0101"),
            "end_de": datetime.now().strftime("%Y%m%d"),
            "page_count": 10
        }

        try:
            response = requests.get(url, params=params)
            print("[DEBUG] 요청 URL:", response.url)
            print("[DEBUG] 응답 상태코드:", response.status_code)
            print("[DEBUG] 응답본문 일부:", response.text[:100])

            if response.status_code != 200:
                return {"error": f"HTTP 오류: {response.status_code}"}

            data = response.json()

            if data.get("status") == "000":
                return {"corp_code": corp_code, "data": data.get("list", [])}
            else:
                return {
                    "error": f"DART 응답 오류: {data.get('message', '알 수 없음')}",
                    "status": data.get("status"),
                    "raw": data
                }

        except Exception as e:
            return {"error": f"DART API 요청 실패: {str(e)}"}