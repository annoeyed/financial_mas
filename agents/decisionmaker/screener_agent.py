import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import yfinance as yf
from api.yfinance_api import get_bulk_volume_parallel, get_bulk_rsi_parallel
import time

class ScreeningAgent:
    def __init__(self):
        self.krx_path = "datapool/krx_stocks.csv"
        self.market_suffix = ".KS"

    def _get_filtered_symbols(self, limit_symbols=100):
        """안정적인 종목들만 필터링하여 반환"""
        try:
            df_krx = pd.read_csv(self.krx_path, encoding="euc-kr")
            
            # 기본 필터링
            df_krx = df_krx[~df_krx["회사명"].str.contains("스팩|리츠", na=False)]
            df_krx["상장일"] = pd.to_datetime(df_krx["상장일"], errors="coerce")
            df_krx = df_krx[df_krx["상장일"].dt.date < (datetime.now().date() - timedelta(days=90))]
            df_krx["종목코드"] = df_krx["종목코드"].astype(str).str.zfill(6)
            df_krx = df_krx[df_krx["종목코드"].str.match(r"^\d{6}$")]
            
            # 안정적인 대형주들만 선택 (상위 20개)
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
            date_range = clarified_query.get("date_range")
            if date_range:
                prev_date = datetime.strptime(date_range["from"], "%Y-%m-%d").date()
                date = datetime.strptime(date_range["to"], "%Y-%m-%d").date()
            else:
                date = datetime.strptime(clarified_query["date"], "%Y-%m-%d").date()
                prev_date = date - timedelta(days=1)

            date_str = date.strftime("%Y-%m-%d")
            volume_threshold = self._parse_volume_change(
                clarified_query.get("condition", {}).get("volume_change") or "0%"
            )
            volume_direction = clarified_query.get("condition", {}).get("volume_direction")
            rsi_threshold = clarified_query.get("condition", {}).get("rsi")
            rsi_threshold = int(''.join(filter(str.isdigit, rsi_threshold))) if rsi_threshold else None
            limit = clarified_query.get("limit", 10)

            if volume_direction not in ["up", "down"]:
                return {"error": "거래량 변화 방향(up/down)이 명확하지 않습니다."}

            # 안정적인 종목들만 선택
            symbols, df_krx = self._get_filtered_symbols(limit_symbols=50)
            
            print(f"분석 대상 종목 수: {len(symbols)}")

            # API 리밋 방지를 위해 순차적으로 처리
            print(f"거래량 데이터 수집 중... (전날: {prev_date.strftime('%Y-%m-%d')})")
            volume_prev_map = get_bulk_volume_parallel(symbols, prev_date.strftime("%Y-%m-%d"), workers=3)
            
            print(f"거래량 데이터 수집 중... (당일: {date.strftime('%Y-%m-%d')})")
            volume_curr_map = get_bulk_volume_parallel(symbols, date.strftime("%Y-%m-%d"), workers=3)
            
            rsi_map = {}
            if rsi_threshold:
                print(f"RSI 데이터 수집 중... (기준일: {date_str})")
                rsi_map = get_bulk_rsi_parallel(symbols, date_str, workers=3)

            matched = []

            def volume_screening(symbol):
                try:
                    code = symbol.replace(".KS", "")
                    # 종목명 찾기
                    name = "Unknown"
                    if not df_krx.empty:
                        name_row = df_krx[df_krx["종목코드"] == code]
                        if not name_row.empty:
                            name = name_row.iloc[0]["회사명"]
                    
                    vol_prev = volume_prev_map.get(symbol)
                    vol_curr = volume_curr_map.get(symbol)

                    if vol_prev is None or vol_curr is None or vol_prev == 0:
                        return None

                    pct_change = ((vol_curr / vol_prev) - 1) * 100
                    if (volume_direction == "up" and pct_change >= volume_threshold * 100) or \
                       (volume_direction == "down" and pct_change <= -volume_threshold * 100):

                        # RSI 조건 확인
                        if rsi_threshold:
                            rsi = rsi_map.get(symbol)
                            if rsi is None or rsi < rsi_threshold:
                                return None
                        else:
                            rsi = None

                        return {
                            "name": name,
                            "code": code,
                            "volume_yesterday": vol_prev,
                            "volume_today": vol_curr,
                            "change_ratio": round(pct_change, 2),
                            **({"rsi": rsi} if rsi_threshold else {})
                        }
                    return None
                except Exception as e:
                    return None

            # API 리밋 방지를 위해 워커 수를 줄임
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(volume_screening, symbol) for symbol in symbols]
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        matched.append(result)
                        if len(matched) >= limit:
                            break

            direction_kor = "증가" if volume_direction == "up" else "감소"
            summary = f"{date_str} 기준 전날 대비 거래량이 {int(volume_threshold * 100)}% 이상 {direction_kor}한 종목"
            if rsi_threshold:
                summary += f", RSI가 {rsi_threshold} 이상인 종목"

            return {
                "judgment": matched,
                "judgment_summary": f"{summary} {len(matched)}개를 찾았습니다." if matched else f"{summary}은 없습니다.",
                "judgment_type": "screening"
            }

        except Exception as e:
            return {"error": f"스크리닝 중 오류 발생: {str(e)}"}

    def _parse_volume_change(self, text: str) -> float:
        """거래량 변화율 텍스트를 파싱하여 float로 변환"""
        if not text:
            return 0.0
        
        # 숫자만 추출
        import re
        numbers = re.findall(r'\d+\.?\d*', text)
        if numbers:
            return float(numbers[0]) / 100  # 퍼센트를 소수로 변환
        return 0.0