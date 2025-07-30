#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.decisionmaker.signal_agent import SignalAgent
import time

def debug_signal_agent_internal():
    """시그널 에이전트 내부 동작 디버그"""
    print("=== 시그널 에이전트 내부 동작 디버그 ===")
    
    signal_agent = SignalAgent()
    
    # 1. 종목 목록 확인
    print("1. 종목 목록 확인:")
    symbols, df_krx = signal_agent._get_filtered_symbols(limit_symbols=5)
    print(f"선택된 종목 수: {len(symbols)}")
    print(f"종목들: {symbols[:3]}...")
    
    # 2. 실제 쿼리 실행
    print("\n2. 실제 쿼리 실행:")
    test_query = {
        "date": "2024-01-15",
        "period": 50,
        "breakout_threshold": 10,
        "limit": 5
    }
    
    print(f"쿼리: {test_query}")
    
    start_time = time.time()
    result = signal_agent.handle(test_query)
    end_time = time.time()
    
    print(f"소요시간: {end_time - start_time:.2f}초")
    print(f"결과 타입: {type(result)}")
    print(f"결과 키들: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
    
    if 'error' in result:
        print(f"오류: {result['error']}")
    else:
        print(f"성공!")
        print(f"요약: {result.get('judgment_summary')}")
        print(f"찾은 종목 수: {len(result.get('judgment', []))}")
        
        if result.get('judgment'):
            for item in result['judgment']:
                print(f"  - {item}")
        else:
            print("  찾은 종목 없음")

def debug_with_recent_date():
    """최근 날짜로 테스트"""
    print("\n=== 최근 날짜로 테스트 ===")
    
    signal_agent = SignalAgent()
    
    # 최근 날짜들로 테스트
    test_dates = ["2024-12-15", "2024-12-10", "2024-12-05", "2024-11-30"]
    
    for test_date in test_dates:
        print(f"\n날짜: {test_date}")
        
        test_query = {
            "date": test_date,
            "period": 50,
            "breakout_threshold": 5,  # 더 낮은 기준
            "limit": 3
        }
        
        start_time = time.time()
        result = signal_agent.handle(test_query)
        end_time = time.time()
        
        print(f"소요시간: {end_time - start_time:.2f}초")
        
        if 'error' in result:
            print(f"오류: {result['error']}")
        else:
            print(f"성공: {len(result.get('judgment', []))}개 종목 발견")
            if result.get('judgment'):
                for item in result['judgment'][:2]:
                    print(f"  - {item['name']}: {item['breakout_ratio']}% 돌파")
            break

def debug_simple_moving_average():
    """간단한 이동평균 테스트"""
    print("\n=== 간단한 이동평균 테스트 ===")
    
    from api.yfinance_api import get_moving_average_data
    
    symbol = "005930.KS"
    test_dates = ["2024-12-15", "2024-12-10", "2024-12-05"]
    
    for test_date in test_dates:
        print(f"\n날짜: {test_date}")
        
        start_time = time.time()
        ma_data = get_moving_average_data(symbol, test_date, period=50)
        end_time = time.time()
        
        if ma_data:
            print(f" 성공!")
            print(f"  현재가: {ma_data['current_price']:,}원")
            print(f"  이동평균: {ma_data['moving_average']:,.2f}원")
            print(f"  돌파율: {ma_data['breakout_ratio']}%")
            print(f"  소요시간: {end_time - start_time:.2f}초")
            break
        else:
            print(f" 실패 (소요시간: {end_time - start_time:.2f}초)")

if __name__ == "__main__":
    debug_signal_agent_internal()
    debug_with_recent_date()
    debug_simple_moving_average() 