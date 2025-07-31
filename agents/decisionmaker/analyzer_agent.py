from agents.base_agent import BaseAgent
from datetime import datetime, timedelta
import yfinance as yf
from api.yfinance_api import get_price_data, get_volume_data, get_rsi_data

class AnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__("AnalyzerAgent")

    async def handle(self, context: dict) -> dict:
        intent = context.get("intent", {})
        symbol = intent.get("symbol")
        date = intent.get("date")
        condition = intent.get("condition") or {}

        if not symbol:
            return {
                "judgment": None,
                "confidence": 0.0,
                "explanation": "종목 정보가 없습니다."
            }

        symbol_name = symbol.get("raw") if isinstance(symbol, dict) else str(symbol)
        yf_code = symbol.get("yfinance_code") if isinstance(symbol, dict) else f"{symbol}.KS"

        # 1. 단순 주가 조회
        if intent.get("task") == "simple_inquiry":
            try:
                print(f"[DEBUG] AnalyzerAgent에서 get_price_data() 호출 준비: {yf_code} / {date}")
                price = get_price_data(yf_code, date)

                if price is None:
                    return {
                        "judgment": None,
                        "confidence": 0.0,
                        "explanation": f"{symbol_name}의 주가 데이터를 가져올 수 없습니다."
                    }

                return {
                    "judgment": {
                        "price": round(price, 2)
                    },
                    "confidence": 0.95,
                    "explanation": f"{symbol_name}의 {date or '현재'} 종가는 {round(price, 2):,}원입니다."
                }

            except Exception as e:
                return {
                    "judgment": None,
                    "confidence": 0.0,
                    "explanation": f"{symbol_name} 주가 조회 중 오류가 발생했습니다: {str(e)}"
                }

        # 2. RSI 판단
        elif "rsi" in condition:
            rsi = get_rsi_data(yf_code, date)
            if rsi is None:
                return {
                    "judgment": None,
                    "confidence": 0.0,
                    "explanation": "RSI 데이터를 찾을 수 없습니다."
                }

            threshold = int(condition["rsi"].replace(">", ""))
            is_over = rsi > threshold

            return {
                "judgment": {
                    "rsi": rsi,
                    "condition_met": is_over
                },
                "confidence": 0.95,
                "explanation": f"{symbol_name}의 {date} RSI는 {rsi}이며 기준값 {threshold} {'초과' if is_over else '이하'}입니다."
            }

        # 3. 거래량 변화율 판단
        elif "volume_change" in condition:
            today_volume = get_volume_data(yf_code, date)
            yesterday = self.get_previous_date(date)
            y_volume = get_volume_data(yf_code, yesterday)

            if today_volume is None or y_volume is None or y_volume == 0:
                return {
                    "judgment": None,
                    "confidence": 0.0,
                    "explanation": "거래량 비교에 필요한 데이터가 부족합니다."
                }

            ratio = (today_volume / y_volume) * 100
            threshold = float(condition["volume_change"].replace(">", "").replace("%", ""))
            is_exceed = ratio > threshold

            return {
                "judgment": {
                    "volume_yesterday": y_volume,
                    "volume_today": today_volume,
                    "change_ratio": round(ratio, 2),
                    "condition_met": is_exceed
                },
                "confidence": 0.95,
                "explanation": f"{symbol_name}의 거래량은 전일 대비 {round(ratio, 2)}% 증가하였고, 기준 {threshold}% {'초과' if is_exceed else '미만'}입니다."
            }

        # 4. 알 수 없는 조건 → fallback
        return {
            "judgment": None,
            "confidence": 0.0,
            "explanation": "지원하지 않는 조건입니다."
        }

    def get_previous_date(self, date_str: str) -> str:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        prev = d - timedelta(days=1)
        return prev.strftime("%Y-%m-%d")