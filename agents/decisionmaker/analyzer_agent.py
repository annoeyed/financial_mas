from agents.base_agent import BaseAgent
from datetime import datetime, timedelta

class AnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__("AnalyzerAgent")

    async def handle(self, context: dict) -> dict:
        intent = context.get("intent", {})
        symbol = intent.get("symbol")
        date = intent.get("date")
        condition = intent.get("condition") or {}

        data = context.get("data")
        result = {}
        explanation = ""

        if not symbol or not date or not data:
            return {
                "judgment": None,
                "confidence": 0.0,
                "reason": "심볼, 날짜, 데이터가 충분하지 않습니다."
            }

        symbol_name = symbol.get("raw") if isinstance(symbol, dict) else str(symbol)

        # 1. RSI 판단
        if "rsi" in condition:
            rsi = data.get_rsi(symbol, date)
            if rsi is None:
                return {
                    "judgment": None,
                    "confidence": 0.0,
                    "reason": "RSI 데이터를 찾을 수 없습니다."
                }

            threshold = int(condition["rsi"].replace(">", ""))
            is_over = rsi > threshold

            result["rsi"] = rsi
            result["judgment"] = is_over
            explanation = f"{symbol_name}의 {date} RSI는 {rsi}이며 기준값 {threshold} {'초과' if is_over else '이하'}입니다."

        # 2. 거래량 변화율 판단
        elif "volume_change" in condition:
            today_volume = data.get_volume(symbol, date)
            yesterday = self.get_previous_date(date)
            y_volume = data.get_volume(symbol, yesterday)

            if today_volume is None or y_volume is None or y_volume == 0:
                return {
                    "judgment": None,
                    "confidence": 0.0,
                    "reason": "거래량 비교에 필요한 데이터 부족"
                }

            ratio = (today_volume / y_volume) * 100
            threshold = float(condition["volume_change"].replace(">", "").replace("%", ""))
            is_exceed = ratio > threshold

            result["today_volume"] = today_volume
            result["yesterday_volume"] = y_volume
            result["change_ratio"] = round(ratio, 2)
            result["judgment"] = is_exceed
            explanation = f"{symbol_name}의 거래량은 전일 대비 {round(ratio, 2)}% 증가하였고, {threshold}% 기준을 {'초과' if is_exceed else '초과하지 않음'}입니다."

        # 3. 단순 시가 조회
        else:
            price = data.get_price(symbol, date)
            if price is None:
                return {
                    "judgment": None,
                    "confidence": 0.0,
                    "reason": "시가 정보 없음"
                }

            result["price"] = price
            result["judgment"] = True
            explanation = f"{symbol_name}의 {date} 시가는 {price}원입니다."

        return {
            "judgment": result,
            "confidence": 0.95,
            "explanation": explanation
        }

    def get_previous_date(self, date_str: str) -> str:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        prev = d - timedelta(days=1)
        return prev.strftime("%Y-%m-%d")