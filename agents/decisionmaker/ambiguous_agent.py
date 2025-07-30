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

from api.yfinance_api import get_price_data, get_moving_average_data
from utils.cache_manager import CacheManager

class AmbiguousAgent:
    """모호한 의미 해석을 위한 Agent"""
    
    def __init__(self, test_mode=False):
        self.cache_manager = CacheManager()
        self.test_mode = test_mode
        
    def _get_filtered_symbols(self, limit_symbols=20):
        """안정적인 종목들 필터링"""
        try:
            # 직접 안정적인 대형주 20개 반환 (CSV 파일 읽기 오류 방지)
            stable_symbols = [
                "005930", "000660", "035420", "051910", "006400", "035720", "207940",
                "068270", "323410", "051900", "006380", "017670", "015760", "028260",
                "032830", "086790", "055550", "105560", "139480", "024110",
            ]
            
            symbols = [f"{code}.KS" for code in stable_symbols]
            return symbols, None
        except Exception as e:
            print(f"종목 필터링 오류: {e}")
            return [], None
    
    def _calculate_recent_performance(self, symbol: str, days: int = 10) -> Optional[Dict]:
        """최근 성과 계산"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days + 10)  # 여유분
            
            # 캐시 확인
            cache_key = f"recent_perf_{symbol}_{days}"
            cached_data = self.cache_manager.get("recent_performance", symbol, str(days))
            if cached_data is not None:
                return cached_data
            
            # API 호출 (테스트 모드에서는 지연시간 단축)
            if not self.test_mode:
                time.sleep(random.uniform(0.1, 0.3))
            df = yf.download(symbol, start=start_date, end=end_date, progress=False, auto_adjust=False)
            
            if df.empty or len(df) < 2:
                return None
            
            # 최근 데이터
            recent_close = df['Close'].iloc[-1].item()
            past_close = df['Close'].iloc[-min(days, len(df)-1)].item()
            
            # 수익률 계산
            performance = ((recent_close - past_close) / past_close) * 100
            
            result = {
                'symbol': symbol,
                'recent_price': recent_close,
                'past_price': past_close,
                'performance': round(performance, 2),
                'days': days
            }
            
            # 캐시 저장 (JSON 직렬화 가능한 형태로 변환)
            try:
                cache_data = {
                    'symbol': symbol,
                    'recent_price': float(recent_close),
                    'past_price': float(past_close),
                    'performance': round(performance, 2),
                    'days': days
                }
                self.cache_manager.set("recent_performance", symbol, str(days), cache_data)
            except Exception as e:
                print(f"캐시 저장 실패: {e}")
            
            return result
            
        except Exception as e:
            print(f"최근 성과 계산 오류 ({symbol}): {e}")
            return None
    
    def _calculate_peak_drop(self, symbol: str, days: int = 252) -> Optional[Dict]:
        """고점 대비 하락률 계산"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days + 50)  # 여유분
            
            # 캐시 확인
            cached_data = self.cache_manager.get("peak_drop", symbol, str(days))
            if cached_data is not None:
                return cached_data
            
            # API 호출 (테스트 모드에서는 지연시간 단축)
            if not self.test_mode:
                time.sleep(random.uniform(0.1, 0.3))
            df = yf.download(symbol, start=start_date, end=end_date, progress=False, auto_adjust=False)
            
            if df.empty or len(df) < 10:
                return None
            
            # 고점 찾기
            peak_price = df['High'].max().item()
            current_price = df['Close'].iloc[-1].item()
            
            # 하락률 계산
            drop_ratio = ((current_price - peak_price) / peak_price) * 100
            
            result = {
                'symbol': symbol,
                'current_price': current_price,
                'peak_price': peak_price,
                'drop_ratio': round(drop_ratio, 2),
                'days': days
            }
            
            # 캐시 저장 (JSON 직렬화 가능한 형태로 변환)
            try:
                cache_data = {
                    'symbol': symbol,
                    'current_price': float(current_price),
                    'peak_price': float(peak_price),
                    'drop_ratio': round(drop_ratio, 2),
                    'days': days
                }
                self.cache_manager.set("peak_drop", symbol, str(days), cache_data)
            except Exception as e:
                print(f"캐시 저장 실패: {e}")
            
            return result
            
        except Exception as e:
            print(f"고점 하락률 계산 오류 ({symbol}): {e}")
            return None
    
    def _ask_for_clarification(self, query_type: str) -> Dict:
        """되묻기 기능"""
        clarifications = {
            'recent_rise': {
                'message': '어떤 기준으로 "많이 오른" 주식을 찾으시나요?',
                'options': [
                    {'label': '최근 5일 10% 이상 상승', 'value': {'days': 5, 'threshold': 10}},
                    {'label': '최근 10일 20% 이상 상승', 'value': {'days': 10, 'threshold': 20}},
                    {'label': '최근 20일 30% 이상 상승', 'value': {'days': 20, 'threshold': 30}}
                ]
            },
            'peak_drop': {
                'message': '어떤 기준으로 "많이 떨어진" 주식을 찾으시나요?',
                'options': [
                    {'label': '52주 고점 대비 20% 이상 하락', 'value': {'days': 252, 'threshold': -20}},
                    {'label': '52주 고점 대비 30% 이상 하락', 'value': {'days': 252, 'threshold': -30}},
                    {'label': '52주 고점 대비 50% 이상 하락', 'value': {'days': 252, 'threshold': -50}}
                ]
            }
        }
        
        return clarifications.get(query_type, {})
    
    def handle(self, query: Dict) -> Dict:
        """모호한 쿼리 처리"""
        query_type = query.get('type', '')
        
        if query_type == 'recent_rise':
            return self._handle_recent_rise(query)
        elif query_type == 'peak_drop':
            return self._handle_peak_drop(query)
        else:
            return {
                'success': False,
                'message': '지원하지 않는 쿼리 타입입니다.',
                'clarification_needed': True,
                'clarification': {
                    'message': '어떤 종류의 주식을 찾으시나요?',
                    'options': [
                        {'label': '최근 많이 오른 주식', 'value': 'recent_rise'},
                        {'label': '고점 대비 많이 떨어진 주식', 'value': 'peak_drop'}
                    ]
                }
            }
    
    def _handle_recent_rise(self, query: Dict) -> Dict:
        """최근 많이 오른 주식 처리"""
        days = query.get('days', 10)
        threshold = query.get('threshold', 10)
        
        symbols, _ = self._get_filtered_symbols()
        
        results = []
        for symbol in symbols:
            performance = self._calculate_recent_performance(symbol, days)
            if performance and performance['performance'] >= threshold:
                results.append(performance)
        
        # 성과 순으로 정렬
        results.sort(key=lambda x: x['performance'], reverse=True)
        
        return {
            'success': True,
            'type': 'recent_rise',
            'criteria': f'최근 {days}일 {threshold}% 이상 상승',
            'stocks': results[:query.get('limit', 10)],
            'total_found': len(results),
            'user_message': f"최근 {days}일간 {threshold}% 이상 상승한 종목 {len(results)}개를 찾았습니다."
        }
    
    def _handle_peak_drop(self, query: Dict) -> Dict:
        """고점 대비 많이 떨어진 주식 처리"""
        days = query.get('days', 252)
        threshold = query.get('threshold', -20)  # 음수 (하락)
        
        symbols, _ = self._get_filtered_symbols()
        
        results = []
        for symbol in symbols:
            drop_data = self._calculate_peak_drop(symbol, days)
            if drop_data and drop_data['drop_ratio'] <= threshold:  # 하락률이 임계값보다 작음
                results.append(drop_data)
        
        # 하락률 순으로 정렬 (가장 많이 떨어진 순)
        results.sort(key=lambda x: x['drop_ratio'])
        
        return {
            'success': True,
            'type': 'peak_drop',
            'criteria': f'{days}일 고점 대비 {abs(threshold)}% 이상 하락',
            'stocks': results[:query.get('limit', 10)],
            'total_found': len(results),
            'user_message': f"52주 고점 대비 {abs(threshold)}% 이상 하락한 종목 {len(results)}개를 찾았습니다."
        } 