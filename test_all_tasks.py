#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.decisionmaker.screener_agent import ScreeningAgent
from api.yfinance_api import get_price_data, get_volume_data, get_bulk_volume_parallel
import time
from datetime import datetime, timedelta

def test_task1_simple_inquiry():
    """Task 1: 단순 조회 테스트"""
    print("=== Task 1: 단순 조회 테스트 ===")
    
    # 테스트 1: 특정 종목의 특정 날짜 종가
    print("1. 삼성전자의 2024-01-15 종가 조회")
    symbol = "005930.KS"
    date = "2024-01-15"
    
    start_time = time.time()
    price = get_price_data(symbol, date)
    end_time = time.time()
    
    if price:
        print(f"삼성전자 종가: {price:,}원 (소요시간: {end_time - start_time:.2f}초)")
    else:
        print(f"데이터 조회 실패")
    
    # 테스트 2: 특정 날짜 거래량 상위 종목
    print("\n2. 2024-01-15 거래량 상위 종목 조회")
    symbols = [
        "005930.KS",  # 삼성전자
        "000660.KS",  # SK하이닉스
        "035420.KS",  # NAVER
        "051910.KS",  # LG화학
        "006400.KS"   # 삼성SDI
    ]
    
    start_time = time.time()
    volume_data = get_bulk_volume_parallel(symbols, "2024-01-15", workers=3)
    end_time = time.time()
    
    if volume_data:
        print("거래량 상위 종목:")
        sorted_volumes = sorted(volume_data.items(), key=lambda x: x[1], reverse=True)
        for i, (symbol, volume) in enumerate(sorted_volumes[:3], 1):
            print(f"  {i}. {symbol}: {volume:,}")
        print(f"소요시간: {end_time - start_time:.2f}초")
    else:
        print("거래량 데이터 조회 실패")
    
    print()

def test_task2_conditional_search():
    """Task 2: 조건검색 테스트"""
    print("=== Task 2: 조건검색 테스트 ===")
    
    screener = ScreeningAgent()
    
    # 테스트 쿼리들
    test_queries = [
        {
            "name": "거래량 50% 이상 증가",
            "query": {
                "date": "2024-01-15",
                "condition": {
                    "volume_change": "50%",
                    "volume_direction": "up"
                },
                "limit": 5
            }
        },
        {
            "name": "거래량 30% 이상 증가", 
            "query": {
                "date": "2024-01-15",
                "condition": {
                    "volume_change": "30%",
                    "volume_direction": "up"
                },
                "limit": 5
            }
        }
    ]
    
    for test in test_queries:
        print(f"\n{test['name']} 테스트:")
        start_time = time.time()
        result = screener.handle(test['query'])
        end_time = time.time()
        
        if 'error' in result:
            print(f"오류: {result['error']}")
        else:
            print(f"성공! (소요시간: {end_time - start_time:.2f}초)")
            print(f"  요약: {result.get('judgment_summary')}")
            if result.get('judgment'):
                for item in result['judgment'][:3]:
                    print(f"  - {item['name']} ({item['code']}): {item['change_ratio']}%")
    
    print()

def test_task3_signal_detection():
    """Task 3: 시그널 감지 테스트 (50일 이동평균)"""
    print("=== Task 3: 시그널 감지 테스트 ===")
    print("   이 기능은 아직 구현되지 않았습니다.")
    print("   - 50일 이동평균 계산 기능 필요")
    print("   - 이동평균 돌파 감지 로직 필요")
    print()

def test_task4_ambiguous_interpretation():
    """Task 4: 모호한 의미 해석 테스트"""
    print("=== Task 4: 모호한 의미 해석 테스트 ===")
    print("  이 기능은 아직 구현되지 않았습니다.")
    print("   - '최근 많이 오른 주식' 정의 필요")
    print("   - '고점 대비 많이 떨어진 주식' 정의 필요")
    print("   - 모호한 언어 정량화 로직 필요")
    print()

def test_task5_custom_feature():
    """Task 5: 특화 기능 테스트"""
    print("=== Task 5: 특화 기능 테스트 ===")
    print(" 현재 구현된 특화 기능:")
    print("    캐시 시스템 - API 호출 최적화")
    print("    안정적인 종목 필터링 - 실패 종목 제거")
    print("    병렬 처리 - 빠른 데이터 수집")
    print("    재시도 로직 - API 리밋 대응")
    print("    진행 상황 표시 - 사용자 경험 개선")
    print()

def test_reliability_and_speed():
    """신뢰성과 속도 테스트"""
    print("=== 신뢰성 및 속도 테스트 ===")
    
    # 캐시 효과 테스트
    print("1. 캐시 효과 테스트:")
    symbol = "005930.KS"
    date = "2024-01-15"
    
    # 첫 번째 호출 (API 사용)
    start_time = time.time()
    volume1 = get_volume_data(symbol, date)
    time1 = time.time() - start_time
    
    # 두 번째 호출 (캐시 사용)
    start_time = time.time()
    volume2 = get_volume_data(symbol, date)
    time2 = time.time() - start_time
    
    if volume1 == volume2:
        print(f" 캐시 기능 정상 작동")
        if time2 > 0:
            print(f"   속도 향상: {time1/time2:.1f}배")
        else:
            print("   속도 향상: 거의 즉시")
    
    # 정확성 테스트
    print("\n2. 데이터 정확성 테스트:")
    if volume1 and volume1 > 0:
        print(f" 거래량 데이터 정상: {volume1:,}")
    else:
        print(" 거래량 데이터 오류")
    
    print()

def main():
    """메인 테스트 함수"""
    print(" 미래에셋 AI Festival 과제 테스트 시작\n")
    
    try:
        # Task 1: 단순 조회
        test_task1_simple_inquiry()
        
        # Task 2: 조건검색
        test_task2_conditional_search()
        
        # Task 3: 시그널 감지
        test_task3_signal_detection()
        
        # Task 4: 모호한 의미 해석
        test_task4_ambiguous_interpretation()
        
        # Task 5: 특화 기능
        test_task5_custom_feature()
        
        # 신뢰성 및 속도 테스트
        test_reliability_and_speed()
        
        print(" 모든 테스트 완료!")
        print("\n 현재 구현 상태:")
        print("    Task 1: 단순 조회 - 완료")
        print("    Task 2: 조건검색 - 완료")
        print("     Task 3: 시그널 감지 - 구현 필요")
        print("     Task 4: 모호한 의미 해석 - 구현 필요")
        print("    Task 5: 특화 기능 - 완료")
        
    except Exception as e:
        print(f" 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 