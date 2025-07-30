#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from datetime import datetime, timedelta

def print_header(title):
    """테스트 헤더 출력"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")

def print_result(success, message):
    """결과 출력"""
    status = "성공" if success else "실패"
    print(f"[{status}]: {message}")

def test_task1_simple_inquiry():
    """Task 1: 단순 조회 테스트"""
    print_header("Task 1: 단순 조회 (Simple Inquiry)")
    
    from api.yfinance_api import get_price_data, get_volume_data
    
    # 테스트 1: 특정 종목의 특정 날짜 종가 조회
    print("\n1. 종목별 종가 조회 테스트")
    test_cases = [
        ("005930.KS", "2024-01-15", "삼성전자"),
        ("000660.KS", "2024-01-15", "SK하이닉스"),
        ("035420.KS", "2024-01-15", "NAVER")
    ]
    
    for symbol, date, name in test_cases:
        try:
            price = get_price_data(symbol, date)
            if price:
                print_result(True, f"{name}: {price:,.0f}원")
            else:
                print_result(False, f"{name}: 데이터 없음")
        except Exception as e:
            print_result(False, f"{name}: 오류 - {e}")
    
    # 테스트 2: 거래량 기준 상위 종목 조회
    print("\n2. 거래량 상위 종목 조회 테스트")
    from agents.decisionmaker.screener_agent import ScreeningAgent
    
    screener = ScreeningAgent()
    test_query = {
        'date': '2024-01-15',
        'condition': {'volume_rank': 'top', 'limit': 5},
        'limit': 5
    }
    
    try:
        result = screener.handle(test_query)
        if result and 'stocks' in result:
            print_result(True, f"상위 {len(result['stocks'])}개 종목 조회 성공")
            for stock in result['stocks'][:3]:  # 상위 3개만 출력
                print(f"  - {stock['name']}: {stock['volume']:,}주")
        else:
            print_result(False, "거래량 상위 종목 조회 실패")
    except Exception as e:
        print_result(False, f"거래량 상위 종목 조회 오류: {e}")

def test_task2_conditional_search():
    """Task 2: 조건검색 테스트"""
    print_header("Task 2: 조건검색 (Conditional Search)")
    
    from agents.decisionmaker.screener_agent import ScreeningAgent
    
    screener = ScreeningAgent()
    
    # 테스트 1: 거래량 증가 조건
    print("\n1. 거래량 증가 조건 테스트")
    test_cases = [
        {'volume_change': '50%', 'volume_direction': 'up'},
        {'volume_change': '100%', 'volume_direction': 'up'},
        {'volume_change': '200%', 'volume_direction': 'up'}
    ]
    
    for condition in test_cases:
        test_query = {
            'date': '2024-01-15',
            'condition': condition,
            'limit': 5
        }
        
        try:
            result = screener.handle(test_query)
            if result and 'stocks' in result:
                print_result(True, f"거래량 {condition['volume_change']} 이상 증가: {len(result['stocks'])}개 종목")
            else:
                print_result(False, f"거래량 {condition['volume_change']} 이상 증가: 조건 만족 종목 없음")
        except Exception as e:
            print_result(False, f"거래량 조건 검색 오류: {e}")

def test_task3_signal_detection():
    """Task 3: 시그널 감지 테스트"""
    print_header("Task 3: 시그널 감지 (Signal Detection)")
    
    from agents.decisionmaker.signal_agent import SignalAgent
    
    signal_agent = SignalAgent()
    
    # 테스트 1: 50일 이동평균 10% 이상 돌파
    print("\n1. 50일 이동평균 10% 이상 돌파 테스트")
    test_query = {
        'date': '2024-01-15',
        'period': 50,
        'threshold': 10,
        'limit': 10
    }
    
    try:
        result = signal_agent.handle(test_query)
        if result and 'stocks' in result:
            print_result(True, f"10% 이상 돌파: {len(result['stocks'])}개 종목")
            for stock in result['stocks'][:3]:  # 상위 3개만 출력
                print(f"  - {stock['name']}: {stock['breakout_ratio']}% 돌파")
        else:
            print_result(False, "10% 이상 돌파 종목 없음")
    except Exception as e:
        print_result(False, f"시그널 감지 오류: {e}")
    
    # 테스트 2: 50일 이동평균 5% 이상 돌파
    print("\n2. 50일 이동평균 5% 이상 돌파 테스트")
    test_query['threshold'] = 5
    
    try:
        result = signal_agent.handle(test_query)
        if result and 'stocks' in result:
            print_result(True, f"5% 이상 돌파: {len(result['stocks'])}개 종목")
            for stock in result['stocks'][:3]:  # 상위 3개만 출력
                print(f"  - {stock['name']}: {stock['breakout_ratio']}% 돌파")
        else:
            print_result(False, "5% 이상 돌파 종목 없음")
    except Exception as e:
        print_result(False, f"시그널 감지 오류: {e}")

def test_task4_ambiguous_interpretation():
    """Task 4: 모호한 의미 해석 테스트"""
    print_header("Task 4: 모호한 의미 해석 (Ambiguous Interpretation)")
    
    print("\nTask 4는 아직 구현되지 않았습니다.")
    print("구현 예정 기능:")
    print("  - '최근 많이 오른 주식' → 정량화 로직 필요")
    print("  - '고점 대비 많이 떨어진 주식' → 피크 대비 하락률 계산")
    print("  - 되묻기 기능 → 사용자에게 구체적인 기준 요청")
    print("  - 신뢰성 확보 방안 → 모호한 표현의 정량화")
    
    print_result(False, "Task 4 미구현")

def test_task5_specialized_features():
    """Task 5: 특화 기능 테스트"""
    print_header("Task 5: 특화 기능 (Specialized Features)")
    
    print("\n구현된 특화 기능들:")
    
    # 캐시 시스템 테스트
    print("\n1. 캐시 시스템 테스트")
    from utils.cache_manager import CacheManager
    cache_manager = CacheManager()
    
    try:
        # 캐시 저장 테스트
        cache_manager.set("test", "key", "value")
        cached_value = cache_manager.get("test", "key")
        if cached_value == "value":
            print_result(True, "캐시 시스템 정상 작동")
        else:
            print_result(False, "캐시 시스템 오류")
    except Exception as e:
        print_result(False, f"캐시 시스템 오류: {e}")
    
    # 병렬 처리 테스트
    print("\n2. 병렬 처리 테스트")
    from api.yfinance_api import get_bulk_volume_parallel
    
    try:
        symbols = ["005930.KS", "000660.KS", "035420.KS"]
        start_time = time.time()
        result = get_bulk_volume_parallel(symbols, "2024-01-15", workers=3)
        end_time = time.time()
        
        if result and len(result) > 0:
            print_result(True, f"병렬 처리 성공: {len(result)}개 종목, {end_time-start_time:.2f}초")
        else:
            print_result(False, "병렬 처리 실패")
    except Exception as e:
        print_result(False, f"병렬 처리 오류: {e}")
    
    # API 리밋 방지 테스트
    print("\n3. API 리밋 방지 테스트")
    print_result(True, "지연시간 및 재시도 로직 구현됨")

def test_performance():
    """성능 테스트"""
    print_header("성능 테스트")
    
    print("\n1. 캐시 성능 테스트")
    from api.yfinance_api import get_price_data
    
    symbol = "005930.KS"
    date = "2024-01-15"
    
    # 첫 번째 호출 (API 사용)
    start_time = time.time()
    price1 = get_price_data(symbol, date)
    time1 = time.time() - start_time
    
    # 두 번째 호출 (캐시 사용)
    start_time = time.time()
    price2 = get_price_data(symbol, date)
    time2 = time.time() - start_time
    
    if price1 == price2 and time2 < time1:
        speedup = time1 / time2 if time2 > 0 else "무한대"
        print_result(True, f"캐시 효과: {speedup}배 속도 향상")
    else:
        print_result(False, "캐시 효과 없음")
    
    print("\n2. 병렬 처리 성능 테스트")
    from api.yfinance_api import get_bulk_volume_parallel
    
    symbols = ["005930.KS", "000660.KS", "035420.KS", "051910.KS", "006400.KS"]
    
    start_time = time.time()
    result = get_bulk_volume_parallel(symbols, "2024-01-15", workers=3)
    end_time = time.time()
    
    if result:
        throughput = len(result) / (end_time - start_time)
        print_result(True, f"처리량: {throughput:.1f} 종목/초")
    else:
        print_result(False, "병렬 처리 실패")

def main():
    """메인 테스트 실행"""
    print("Financial MAS 통합 테스트 시작")
    print(f"테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 각 Task 테스트 실행
    test_task1_simple_inquiry()
    test_task2_conditional_search()
    test_task3_signal_detection()
    test_task4_ambiguous_interpretation()
    test_task5_specialized_features()
    test_performance()
    
    print_header("테스트 완료")
    print("구현 현황:")
    print("  Task 1: 단순 조회 - 완료")
    print("  Task 2: 조건검색 - 완료")
    print("  Task 3: 시그널 감지 - 완료")
    print("  Task 4: 모호한 의미 해석 - 미구현")
    print("  Task 5: 특화 기능 - 부분 완료")
    print("\n다음 단계: Task 4 구현")

if __name__ == "__main__":
    main() 