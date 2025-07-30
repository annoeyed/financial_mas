#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import yfinance as yf
import time
import random

from api.yfinance_api import get_price_data
from utils.cache_manager import CacheManager

class AdvancedAgent:
    """고급 분석을 위한 Agent"""
    
    def __init__(self, test_mode=False):
        self.cache_manager = CacheManager()
        self.test_mode = test_mode
        
    def _get_filtered_symbols(self, limit_symbols=10):
        """분석 대상 종목들 필터링"""
        try:
            # 주요 대형주 10개
            stable_symbols = [
                "005930", "000660", "035420", "051910", "006400", 
                "035720", "207940", "068270", "323410", "051900"
            ]
            
            symbols = [f"{code}.KS" for code in stable_symbols]
            return symbols
        except Exception as e:
            print(f"종목 필터링 오류: {e}")
            return []
    
    def _get_historical_data(self, symbol: str, days: int = 252) -> Optional[pd.DataFrame]:
        """과거 데이터 수집"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days + 50)
            
            # 캐시 확인 비활성화 (오류 해결을 위해)
            # cache_key = f"historical_{symbol}_{days}"
            # cached_data = self.cache_manager.get("historical", cache_key)
            # if cached_data is not None:
            #     try:
            #         df = pd.DataFrame(cached_data['data'], columns=cached_data['columns'])
            #         df.index = pd.to_datetime(cached_data['index'])
            #         return df
            #     except Exception as e:
            #         print(f"캐시 복원 실패: {e}")
            pass
            
            # API 호출 (테스트 모드에서는 지연시간 단축)
            if not self.test_mode:
                time.sleep(random.uniform(0.1, 0.3))
            
            df = yf.download(symbol, start=start_date, end=end_date, progress=False, auto_adjust=False)
            
            if df.empty:
                return None
            
            # 캐시 저장 비활성화 (오류 해결을 위해)
            # try:
            #     cache_data = {
            #         'data': df.to_dict('records'),
            #         'columns': df.columns.tolist(),
            #         'index': df.index.tolist()
            #     }
            #     cache_key = f"historical_{symbol}_{days}"
            #     self.cache_manager.set("historical", cache_key, cache_data)
            # except Exception as e:
            #     print(f"캐시 저장 실패: {e}")
            pass
            
            return df
            
        except Exception as e:
            print(f"과거 데이터 수집 오류 ({symbol}): {e}")
            return None
    
    def calculate_correlation(self, symbols: List[str], days: int = 60) -> Dict:
        """종목 간 상관관계 분석"""
        try:
            print(f"상관관계 분석 중... ({len(symbols)}개 종목, {days}일)")
            
            # 각 종목의 수익률 데이터 수집
            returns_data = {}
            for symbol in symbols:
                df = self._get_historical_data(symbol, days)
                if df is not None and len(df) > 10:
                    # 일간 수익률 계산
                    returns = df['Close'].pct_change().dropna()
                    returns_data[symbol] = returns
            
            if len(returns_data) < 2:
                return {'success': False, 'message': '분석 가능한 데이터 부족'}
            
            # 상관관계 매트릭스 계산
            if not returns_data:
                return {'success': False, 'error': '수익률 데이터가 없습니다.'}
            
            # 인덱스 정렬을 위해 공통 기간만 사용
            min_length = min(len(returns) for returns in returns_data.values())
            if min_length < 2:
                return {'success': False, 'error': '충분한 데이터가 없습니다.'}
                
            aligned_returns = {}
            for symbol, returns in returns_data.items():
                # 1차원 배열로 변환
                aligned_returns[symbol] = returns.tail(min_length).values.flatten()
            
            returns_df = pd.DataFrame(aligned_returns)
            correlation_matrix = returns_df.corr()
            
            # 높은 상관관계 쌍 찾기 (0.7 이상)
            high_corr_pairs = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    corr_value = correlation_matrix.iloc[i, j]
                    if abs(corr_value) >= 0.7:
                        high_corr_pairs.append({
                            'symbol1': correlation_matrix.columns[i],
                            'symbol2': correlation_matrix.columns[j],
                            'correlation': round(corr_value, 3)
                        })
            
            return {
                'success': True,
                'correlation_matrix': correlation_matrix.to_dict(),
                'high_correlation_pairs': high_corr_pairs,
                'total_pairs': len(high_corr_pairs)
            }
            
        except Exception as e:
            return {'success': False, 'message': f'상관관계 분석 오류: {e}'}
    
    def calculate_volatility(self, symbols: List[str], days: int = 60) -> Dict:
        """변동성 분석"""
        try:
            print(f"변동성 분석 중... ({len(symbols)}개 종목, {days}일)")
            
            # 변동성 계산
            volatility_data = {}
            for symbol in symbols:
                df = self._get_historical_data(symbol, days)
                if df is not None and len(df) > 1:
                    returns = df['Close'].pct_change().dropna()
                    volatility = returns.std().item() * np.sqrt(252) * 100
                    volatility_data[symbol] = volatility
            
            # 변동성 순으로 정렬
            volatility_results = sorted(volatility_data.items(), key=lambda item: item[1], reverse=True)
            
            return {
                'success': True,
                'volatility_ranking': [{'symbol': s, 'volatility': v} for s, v in volatility_results],
                'high_volatility': [{'symbol': s, 'volatility': v} for s, v in volatility_results if v > 30],
                'low_volatility': [{'symbol': s, 'volatility': v} for s, v in volatility_results if v < 15]
            }
            
        except Exception as e:
            return {'success': False, 'message': f'변동성 분석 오류: {e}'}
    
    def calculate_momentum(self, symbols: List[str], periods: List[int] = [5, 10, 20]) -> Dict:
        """모멘텀 분석"""
        try:
            print(f"모멘텀 분석 중... ({len(symbols)}개 종목)")
            
            momentum_results = []
            for symbol in symbols:
                df = self._get_historical_data(symbol, max(periods) + 30)
                if df is not None and len(df) > max(periods):
                    current_price = df['Close'].iloc[-1].item()
                    momentum_scores = {}
                    
                    for period in periods:
                        if len(df) > period:
                            past_price = df['Close'].iloc[-period].item()
                            momentum = ((current_price - past_price) / past_price) * 100
                            momentum_scores[f'{period}일'] = round(momentum, 2)
                    
                    # 종합 모멘텀 점수 (가중 평균)
                    if momentum_scores:
                        weights = [0.5, 0.3, 0.2]  # 5일, 10일, 20일 가중치
                        weighted_momentum = sum(
                            momentum_scores[f'{period}일'] * weight 
                            for period, weight in zip(periods, weights)
                            if f'{period}일' in momentum_scores
                        )
                        
                        momentum_results.append({
                            'symbol': symbol,
                            'current_price': current_price,
                            'momentum_scores': momentum_scores,
                            'weighted_momentum': round(weighted_momentum, 2)
                        })
            
            # 모멘텀 순으로 정렬
            momentum_results.sort(key=lambda x: x['weighted_momentum'], reverse=True)
            
            return {
                'success': True,
                'momentum_ranking': momentum_results,
                'strong_momentum': [m for m in momentum_results if m['weighted_momentum'] > 10],
                'weak_momentum': [m for m in momentum_results if m['weighted_momentum'] < -5]
            }
            
        except Exception as e:
            return {'success': False, 'message': f'모멘텀 분석 오류: {e}'}
    
    def portfolio_optimization(self, symbols: List[str], target_return: float = 0.1) -> Dict:
        """간단한 포트폴리오 최적화"""
        try:
            print(f"포트폴리오 최적화 중... ({len(symbols)}개 종목)")
            
            # 각 종목의 수익률과 변동성 계산
            portfolio_data = []
            for symbol in symbols:
                df = self._get_historical_data(symbol, 252)
                if df is not None and len(df) > 60:
                    returns = df['Close'].pct_change().dropna()
                    
                    # 연간 수익률과 변동성
                    annual_return = returns.mean().item() * 252 * 100
                    annual_volatility = returns.std().item() * np.sqrt(252) * 100
                    
                    portfolio_data.append({
                        'symbol': symbol,
                        'return': round(annual_return, 2),
                        'volatility': round(annual_volatility, 2),
                        'sharpe_ratio': round(annual_return / annual_volatility, 3) if annual_volatility > 0 else 0
                    })
            
            # 샤프 비율 순으로 정렬
            portfolio_data.sort(key=lambda x: x['sharpe_ratio'], reverse=True)
            
            # 최적 포트폴리오 (상위 5개)
            optimal_portfolio = portfolio_data[:5]
            
            return {
                'success': True,
                'optimal_portfolio': optimal_portfolio,
                'total_analyzed': len(portfolio_data),
                'recommendation': f"샤프 비율 기준 상위 {len(optimal_portfolio)}개 종목 추천"
            }
            
        except Exception as e:
            return {'success': False, 'message': f'포트폴리오 최적화 오류: {e}'}
    
    def handle(self, query: Dict) -> Dict:
        """고급 분석 쿼리 처리"""
        analysis_type = query.get('type', '')
        
        symbols = self._get_filtered_symbols()
        
        if analysis_type == 'correlation':
            return self.calculate_correlation(symbols, query.get('days', 60))
        elif analysis_type == 'volatility':
            return self.calculate_volatility(symbols, query.get('days', 60))
        elif analysis_type == 'momentum':
            return self.calculate_momentum(symbols, query.get('periods', [5, 10, 20]))
        elif analysis_type == 'portfolio':
            return self.portfolio_optimization(symbols, query.get('target_return', 0.1))
        else:
            return {
                'success': False,
                'message': '지원하지 않는 분석 타입입니다.',
                'available_types': ['correlation', 'volatility', 'momentum', 'portfolio']
            } 