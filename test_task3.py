#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.decisionmaker.signal_agent import SignalAgent
from api.yfinance_api import get_moving_average_data
import time

def test_single_moving_average():
    """단일 종목 이동평균 테스트"""
    print("=== 단일 종목 이동평균 테스트 ===")
    
    symbol = "005930.KS"  # 삼성전자
    test_date = "2024-01-15"
    
    print(f"테스트 종목: {symbol}")
    print(f"테스트 날짜: {test_date}")
    
    # 병렬 처리 함수 사용
    from api.yfinance_api import get_bulk_moving_average_parallel
    
    start_time = time.time()
    ma_data_map = get_bulk_moving_average_parallel([symbol], test_date, period=50, workers=1)
    end_time = time.time()
    
    ma_data = ma_data_map.get(symbol)
    
    if ma_data:
        print(f" 이동평균 데이터:")
        print(f"  현재가: {ma_data['current_price']:,}원")
        print(f"  50일 이동평균: {ma_data['moving_average']:,.2f}원")
        print(f"  돌파율: {ma_data['breakout_ratio']}%")
        print(f"  돌파 여부: {'예' if ma_data['is_breakout'] else '아니오'}")
        print(f"  소요시간: {end_time - start_time:.2f}초")
    else:
        print(f" 데이터 조회 실패")
        print(f"  가능한 원인:")
        print(f"    - 해당 날짜에 거래 데이터 없음")
        print(f"    - 50일 이동평균 계산을 위한 데이터 부족")
        print(f"    - API 리밋 또는 네트워크 문제")
    
    print()

def test_single_moving_average_recent():
    """최근 날짜로 단일 종목 이동평균 테스트"""
    print("=== 최근 날짜 이동평균 테스트 ===")
    
    symbol = "005930.KS"  # 삼성전자
    # 더 최근 날짜 사용
    test_date = "2024-12-15"  # 더 최근 날짜
    
    print(f"테스트 종목: {symbol}")
    print(f"테스트 날짜: {test_date}")
    
    # 병렬 처리 함수 사용
    from api.yfinance_api import get_bulk_moving_average_parallel
    
    start_time = time.time()
    ma_data_map = get_bulk_moving_average_parallel([symbol], test_date, period=50, workers=1)
    end_time = time.time()
    
    ma_data = ma_data_map.get(symbol)
    
    if ma_data:
        print(f" 이동평균 데이터:")
        print(f"  현재가: {ma_data['current_price']:,}원")
        print(f"  50일 이동평균: {ma_data['moving_average']:,.2f}원")
        print(f"  돌파율: {ma_data['breakout_ratio']}%")
        print(f"  돌파 여부: {'예' if ma_data['is_breakout'] else '아니오'}")
        print(f"  소요시간: {end_time - start_time:.2f}초")
    else:
        print(f" 데이터 조회 실패")
        print(f"  다른 날짜로 재시도 중...")
        
        # 다른 날짜들로 재시도
        test_dates = ["2024-12-10", "2024-12-05", "2024-11-30"]
        for retry_date in test_dates:
            print(f"  {retry_date} 시도 중...")
            ma_data_map = get_bulk_moving_average_parallel([symbol], retry_date, period=50, workers=1)
            ma_data = ma_data_map.get(symbol)
            if ma_data:
                print(f" 성공! {retry_date} 기준:")
                print(f"    현재가: {ma_data['current_price']:,}원")
                print(f"    돌파율: {ma_data['breakout_ratio']}%")
                break
        else:
            print(f"  모든 날짜에서 실패")
    
    print()

def test_signal_agent():
    """시그널 에이전트 테스트"""
    print("=== 시그널 에이전트 테스트 ===")
    
    signal_agent = SignalAgent()
    
    # 테스트 쿼리들
    test_queries = [
        {
            "name": "50일 이동평균 10% 이상 돌파",
            "query": {
                "date": "2024-01-15",
                "period": 50,
                "breakout_threshold": 10,
                "limit": 5
            }
        },
        {
            "name": "50일 이동평균 5% 이상 돌파",
            "query": {
                "date": "2024-01-15",
                "period": 50,
                "breakout_threshold": 5,
                "limit": 5
            }
        }
    ]
    
    for test in test_queries:
        print(f"\n{test['name']} 테스트:")
        start_time = time.time()
        result = signal_agent.handle(test['query'])
        end_time = time.time()
        
        if 'error' in result:
            print(f" 오류: {result['error']}")
        else:
            print(f" 성공! (소요시간: {end_time - start_time:.2f}초)")
            print(f"  요약: {result.get('judgment_summary')}")
            if result.get('judgment'):
                for item in result['judgment'][:3]:
                    print(f"  - {item['name']} ({item['code']}): {item['breakout_ratio']}% 돌파")
                    print(f"    현재가: {item['current_price']:,}원, 이동평균: {item['moving_average']:,.2f}원")
    
    print()

def test_different_periods():
    """다른 기간 이동평균 테스트"""
    print("=== 다른 기간 이동평균 테스트 ===")
    
    symbol = "005930.KS"
    test_date = "2024-01-15"
    periods = [20, 50, 100]
    
    # 병렬 처리 함수 사용
    from api.yfinance_api import get_bulk_moving_average_parallel
    
    for period in periods:
        print(f"\n{period}일 이동평균 테스트:")
        start_time = time.time()
        ma_data_map = get_bulk_moving_average_parallel([symbol], test_date, period=period, workers=1)
        end_time = time.time()
        
        ma_data = ma_data_map.get(symbol)
        
        if ma_data:
            print(f"   현재가: {ma_data['current_price']:,}원")
            print(f"  {period}일 이동평균: {ma_data['moving_average']:,.2f}원")
            print(f"  돌파율: {ma_data['breakout_ratio']}%")
            print(f"  소요시간: {end_time - start_time:.2f}초")
        else:
            print(f"   데이터 조회 실패")
    
    print()

def main():
    """메인 테스트 함수"""
    print(" Task 3: 시그널 감지 테스트 시작\n")
    
    try:
        # 1. 단일 종목 이동평균 테스트 (기존 날짜)
        test_single_moving_average()
        
        # 2. 최근 날짜로 재시도
        test_single_moving_average_recent()
        
        # 3. 다른 기간 이동평균 테스트
        test_different_periods()
        
        # 4. 시그널 에이전트 테스트
        test_signal_agent()
        
        print(" Task 3 테스트 완료!")
        print("\n 구현된 기능:")
        print("    이동평균 계산")
        print("    돌파율 계산")
        print("    병렬 처리")
        print("    캐시 시스템")
        print("    안정적인 종목 필터링")
        
    except Exception as e:
        print(f" 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 