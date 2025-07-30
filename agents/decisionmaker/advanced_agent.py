from agents.base_agent import BaseAgent
from datetime import datetime, timedelta
from utils.cache_manager import CacheManager
import yfinance as yf
import pandas as pd
import numpy as np
import time
import random


class AdvancedAgent(BaseAgent):
    def __init__(self, test_mode=False):
        super().__init__("AdvancedAgent")
        self.cache_manager = CacheManager()
        self.test_mode = test_mode

    async def handle(self, context: dict) -> dict:
        intent = context.get("intent", {})
        analysis_type = intent.get("type", "")
        symbols = self._get_filtered_symbols()

        if analysis_type == "correlation":
            return self.calculate_correlation(symbols, intent.get("days", 60))
        elif analysis_type == "volatility":
            return self.calculate_volatility(symbols, intent.get("days", 60))
        elif analysis_type == "momentum":
            return self.calculate_momentum(symbols, intent.get("periods", [5, 10, 20]))
        elif analysis_type == "portfolio":
            return self.portfolio_optimization(symbols, intent.get("target_return", 0.1))
        else:
            return {
                "success": False,
                "judgment_type": "advanced_analysis",
                "judgment_summary": "지원하지 않는 분석 유형입니다.",
                "available_types": ["correlation", "volatility", "momentum", "portfolio"]
            }

    def _get_filtered_symbols(self, limit=10):
        stable = [
            "005930", "000660", "035420", "051910", "006400",
            "035720", "207940", "068270", "323410", "051900"
        ]
        return [f"{code}.KS" for code in stable][:limit]

    def _get_historical_data(self, symbol: str, days: int = 252):
        try:
            end_date = datetime.today().date()
            start_date = end_date - timedelta(days=days + 50)

            if not self.test_mode:
                time.sleep(random.uniform(0.1, 0.3))

            df = yf.download(symbol, start=start_date, end=end_date, progress=False)
            if df.empty:
                return None
            return df
        except:
            return None

    def calculate_correlation(self, symbols, days=60):
        returns_data = {}
        for symbol in symbols:
            df = self._get_historical_data(symbol, days)
            if df is not None and len(df) > 10:
                returns = df['Close'].pct_change().dropna()
                returns_data[symbol] = returns

        if len(returns_data) < 2:
            return {"success": False, "judgment_type": "correlation", "judgment_summary": "분석 가능한 데이터 부족"}

        min_len = min(len(r) for r in returns_data.values())
        aligned = {s: r.tail(min_len).values.flatten() for s, r in returns_data.items()}
        returns_df = pd.DataFrame(aligned)
        corr_matrix = returns_df.corr()

        pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr = corr_matrix.iloc[i, j]
                if abs(corr) >= 0.7:
                    pairs.append({
                        "symbol1": corr_matrix.columns[i],
                        "symbol2": corr_matrix.columns[j],
                        "correlation": round(corr, 3)
                    })

        return {
            "success": True,
            "judgment_type": "correlation",
            "judgment_summary": f"상관계수 0.7 이상인 종목 쌍 {len(pairs)}개",
            "correlation_matrix": corr_matrix.to_dict(),
            "high_correlation_pairs": pairs
        }

    def calculate_volatility(self, symbols, days=60):
        vol_data = {}
        for symbol in symbols:
            df = self._get_historical_data(symbol, days)
            if df is not None and len(df) > 1:
                returns = df["Close"].pct_change().dropna()
                vol = returns.std() * np.sqrt(252) * 100
                vol_data[symbol] = vol

        ranking = sorted(vol_data.items(), key=lambda x: x[1], reverse=True)

        return {
            "success": True,
            "judgment_type": "volatility",
            "judgment_summary": f"변동성 분석 완료 (총 {len(ranking)}개 종목)",
            "volatility_ranking": [{"symbol": s, "volatility": round(v, 2)} for s, v in ranking]
        }

    def calculate_momentum(self, symbols, periods=[5, 10, 20]):
        results = []
        for symbol in symbols:
            df = self._get_historical_data(symbol, max(periods) + 30)
            if df is not None and len(df) > max(periods):
                current = df["Close"].iloc[-1]
                scores = {}
                for p in periods:
                    if len(df) > p:
                        past = df["Close"].iloc[-p]
                        scores[f"{p}일"] = round(((current - past) / past) * 100, 2)

                if scores:
                    weights = [0.5, 0.3, 0.2]
                    weighted = sum(
                        scores[f"{p}일"] * w
                        for p, w in zip(periods, weights)
                        if f"{p}일" in scores
                    )
                    results.append({
                        "symbol": symbol,
                        "momentum_scores": scores,
                        "weighted_momentum": round(weighted, 2)
                    })

        results.sort(key=lambda x: x["weighted_momentum"], reverse=True)

        return {
            "success": True,
            "judgment_type": "momentum",
            "judgment_summary": f"모멘텀 분석 완료 (상위 {len(results)}개)",
            "momentum_ranking": results
        }

    def portfolio_optimization(self, symbols, target_return=0.1):
        data = []
        for symbol in symbols:
            df = self._get_historical_data(symbol, 252)
            if df is not None and len(df) > 60:
                returns = df["Close"].pct_change().dropna()
                annual_return = returns.mean() * 252 * 100
                annual_vol = returns.std() * np.sqrt(252) * 100
                sharpe = annual_return / annual_vol if annual_vol > 0 else 0

                data.append({
                    "symbol": symbol,
                    "return": round(annual_return, 2),
                    "volatility": round(annual_vol, 2),
                    "sharpe_ratio": round(sharpe, 3)
                })

        data.sort(key=lambda x: x["sharpe_ratio"], reverse=True)
        top = data[:5]

        return {
            "success": True,
            "judgment_type": "portfolio",
            "judgment_summary": f"샤프 비율 기준 상위 {len(top)}개 포트폴리오 추천",
            "optimal_portfolio": top
        }