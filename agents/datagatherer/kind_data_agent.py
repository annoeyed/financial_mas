import os
import pandas as pd
from agents.base_agent import BaseAgent

KIND_CSV_FILE = "KIND_corp_list.csv"

class KINDDataAgent(BaseAgent):
    def __init__(self):
        super().__init__("KINDDataAgent")
        self.corp_df = self._load_kind_data()

    def _load_kind_data(self):
        """
        KIND에서 받은 CSV 파일을 읽어 DataFrame으로 반환
        """
        if not os.path.exists(KIND_CSV_FILE):
            raise FileNotFoundError(f"{KIND_CSV_FILE} 파일이 없습니다. KIND에서 다운로드 후 저장해 주세요.")

        try:
            df = pd.read_csv(KIND_CSV_FILE, encoding="utf-8")  # EUC-KR 인코딩 사용
            df = df.rename(columns=lambda x: x.strip())  # 컬럼명 공백 제거
            return df
        except Exception as e:
            raise RuntimeError(f"KIND CSV 파일을 불러오는데 실패했습니다: {e}")

    def process(self, structured: dict) -> dict:
        """
        structured 딕셔너리에서 'target' 값을 받아 종목코드 조회
        """
        target = structured.get("target", "").strip()
        if not target:
            return {"error": "기업명을 입력해주세요."}

        matches = self.corp_df[self.corp_df["회사명"].str.contains(target, na=False)]

        if matches.empty:
            return {"error": f"'{target}' 에 해당하는 상장회사를 찾을 수 없습니다."}
        else:
            result = matches[["회사명", "종목코드"]].to_dict(orient="records")
            return {"matches": result}