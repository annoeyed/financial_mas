import os
import requests
import zipfile
import io
from dotenv import load_dotenv

load_dotenv()

DART_API_KEY = os.getenv("DART_API_KEY")
CORPCODE_URL = f"https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key={DART_API_KEY}"
CORPCODE_FILE = "CORPCODE.xml"

def download_and_extract_corp_code(force=False):
    if os.path.exists(CORPCODE_FILE) and not force:
        print(f"[INFO] 이미 {CORPCODE_FILE} 파일이 존재합니다.")
        return

    response = requests.get(CORPCODE_URL)
    print("[DEBUG] 응답코드:", response.status_code)

    if response.status_code == 200:
        try:
            with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
                zf.extract(CORPCODE_FILE)
                print(f"[INFO] {CORPCODE_FILE} 압축 해제 완료")
        except zipfile.BadZipFile:
            print("[ERROR] 받은 파일이 유효한 zip 파일이 아닙니다.")
            print("[DEBUG] 응답본문 앞부분:", response.content[:200])
    else:
        print(f"[ERROR] 다운로드 실패: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    download_and_extract_corp_code(force=True)