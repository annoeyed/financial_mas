import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from api.yfinance_api import get_bulk_moving_average_parallel
import time

class SignalAgent:
    def __init__(self):
        self.krx_path = "datapool/krx_stocks.csv"
        self.market_suffix = ".KS"

    def _get_filtered_symbols(self, limit_symbols=20):
        """안정적인 종목들만 필터링하여 반환"""
        try:
            df_krx = pd.read_csv(self.krx_path, encoding="euc-kr")
            
            # 기본 필터링
            df_krx = df_krx[~df_krx["회사명"].str.contains("스팩|리츠", na=False)]
            df_krx["상장일"] = pd.to_datetime(df_krx["상장일"], errors="coerce")
            df_krx = df_krx[df_krx["상장일"].dt.date < (datetime.now().date() - timedelta(days=90))]
            df_krx["종목코드"] = df_krx["종목코드"].astype(str).str.zfill(6)
            df_krx = df_krx[df_krx["종목코드"].str.match(r"^\d{6}$")]
            
            # 안정적인 대형주들만 선택
            stable_symbols = [
                "005930",  # 삼성전자
                "000660",  # SK하이닉스
                "035420",  # NAVER
                "051910",  # LG화학
                "006400",  # 삼성SDI
                "035720",  # 카카오
                "207940",  # 삼성바이오로직스
                "068270",  # 셀트리온
                "323410",  # 카카오뱅크
                "051900",  # LG생활건강
                "006380",  # 카프리
                "017670",  # SK텔레콤
                "015760",  # 한국전력
                "028260",  # 삼성물산
                "032830",  # 삼성생명
                "086790",  # 하나금융지주
                "055550",  # 신한지주
                "105560",  # KB금융
                "139480",  # 이마트
                "024110",  # 기업은행
            ]
            
            # 안정적인 종목들만 필터링
            df_filtered = df_krx[df_krx["종목코드"].isin(stable_symbols)]
            
            if df_filtered.empty:
                # 기본 종목들 사용
                symbols = [code + self.market_suffix for code in stable_symbols]
                return symbols, pd.DataFrame()
            
            symbols = [row["종목코드"] + self.market_suffix for _, row in df_filtered.iterrows()]
            return symbols, df_filtered
            
        except Exception as e:
            print(f"종목 목록 로드 실패: {e}")
            # 기본 종목들 (대형주 위주)
            default_symbols = [
                "005930.KS",  # 삼성전자
                "000660.KS",  # SK하이닉스
                "035420.KS",  # NAVER
                "051910.KS",  # LG화학
                "006400.KS",  # 삼성SDI
                "035720.KS",  # 카카오
                "207940.KS",  # 삼성바이오로직스
                "068270.KS",  # 셀트리온
                "323410.KS",  # 카카오뱅크
                "051900.KS"   # LG생활건강
            ]
            return default_symbols, pd.DataFrame()

    def handle(self, clarified_query: dict) -> dict:
        try:
            date = datetime.strptime(clarified_query["date"], "%Y-%m-%d").date()
            date_str = date.strftime("%Y-%m-%d")
            period = clarified_query.get("period", 50)  # 기본 50일
            breakout_threshold = clarified_query.get("breakout_threshold", 10)  # 기본 10%
            limit = clarified_query.get("limit", 10)

            # 안정적인 종목들만 선택
            symbols, df_krx = self._get_filtered_symbols(limit_symbols=20)
            
            print(f"분석 대상 종목 수: {len(symbols)}")
            print(f"이동평균 기간: {period}일")
            print(f"돌파 기준: {breakout_threshold}%")

            # 이동평균 데이터 수집
            print(f"이동평균 데이터 수집 중... (기준일: {date_str})")
            ma_data_map = get_bulk_moving_average_parallel(symbols, date_str, period=period, workers=3)

            matched = []

            def signal_screening(symbol):
                try:
                    code = symbol.replace(".KS", "")
                    # 종목명 찾기
                    name = "Unknown"
                    if not df_krx.empty:
                        name_row = df_krx[df_krx["종목코드"] == code]
                        if not name_row.empty:
                            name = name_row.iloc[0]["회사명"]
                    
                    ma_data = ma_data_map.get(symbol)
                    if ma_data is None:
                        return None

                    # 돌파 조건 확인
                    if ma_data['is_breakout'] and ma_data['breakout_ratio'] >= breakout_threshold:
                        return {
                            "name": name,
                            "code": code,
                            "current_price": ma_data['current_price'],
                            "moving_average": ma_data['moving_average'],
                            "breakout_ratio": ma_data['breakout_ratio']
                        }
                    return None
                except Exception as e:
                    return None

            # API 리밋 방지를 위해 워커 수를 줄임
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(signal_screening, symbol) for symbol in symbols]
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        matched.append(result)
                        if len(matched) >= limit:
                            break

            # 결과 정렬 (돌파율 높은 순)
            matched.sort(key=lambda x: x['breakout_ratio'], reverse=True)

            summary = f"{date_str} 기준 {period}일 이동평균을 {breakout_threshold}% 이상 상향 돌파한 종목"

            return {
                "judgment": matched,
                "judgment_summary": f"{summary} {len(matched)}개를 찾았습니다." if matched else f"{summary}은 없습니다.",
                "judgment_type": "signal_detection"
            }

        except Exception as e:
            return {"error": f"시그널 감지 중 오류 발생: {str(e)}"} 