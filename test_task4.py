#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from datetime import datetime

def test_ambiguous_agent():
    """Task 4: 모호한 의미 해석 테스트"""
    print("Task 4: 모호한 의미 해석 테스트 시작")
    
    from agents.decisionmaker.ambiguous_agent import AmbiguousAgent
    
    agent = AmbiguousAgent(test_mode=True)  # 테스트 모드로 빠른 실행
    
    # 테스트 1: 최근 많이 오른 주식
    print("\n1. 최근 많이 오른 주식 테스트")
    
    test_cases = [
        {'days': 5, 'threshold': 5, 'description': '최근 5일 5% 이상 상승'},
        {'days': 10, 'threshold': 10, 'description': '최근 10일 10% 이상 상승'},
        {'days': 20, 'threshold': 15, 'description': '최근 20일 15% 이상 상승'}
    ]
    
    for case in test_cases:
        query = {
            'type': 'recent_rise',
            'days': case['days'],
            'threshold': case['threshold'],
            'limit': 5
        }
        
        print(f"\n{case['description']}:")
        start_time = time.time()
        result = agent.handle(query)
        end_time = time.time()
        
        if result['success']:
            print(f"  성공! {result['total_found']}개 종목 발견")
            for stock in result['stocks'][:3]:  # 상위 3개만 출력
                print(f"  - {stock['symbol']}: {stock['performance']}% 상승")
            print(f"  소요시간: {end_time - start_time:.2f}초")
        else:
            print(f"  실패: {result.get('message', '알 수 없는 오류')}")
    
    # 테스트 2: 고점 대비 많이 떨어진 주식
    print("\n2. 고점 대비 많이 떨어진 주식 테스트")
    
    test_cases = [
        {'days': 252, 'threshold': -10, 'description': '52주 고점 대비 10% 이상 하락'},
        {'days': 252, 'threshold': -20, 'description': '52주 고점 대비 20% 이상 하락'},
        {'days': 252, 'threshold': -30, 'description': '52주 고점 대비 30% 이상 하락'}
    ]
    
    for case in test_cases:
        query = {
            'type': 'peak_drop',
            'days': case['days'],
            'threshold': case['threshold'],
            'limit': 5
        }
        
        print(f"\n{case['description']}:")
        start_time = time.time()
        result = agent.handle(query)
        end_time = time.time()
        
        if result['success']:
            print(f"  성공! {result['total_found']}개 종목 발견")
            for stock in result['stocks'][:3]:  # 상위 3개만 출력
                print(f"  - {stock['symbol']}: {stock['drop_ratio']}% 하락")
            print(f"  소요시간: {end_time - start_time:.2f}초")
        else:
            print(f"  실패: {result.get('message', '알 수 없는 오류')}")
    
    # 테스트 3: 되묻기 기능
    print("\n3. 되묻기 기능 테스트")
    
    # 잘못된 쿼리로 되묻기 테스트
    query = {'type': 'invalid_type'}
    result = agent.handle(query)
    
    if result.get('clarification_needed'):
        print("  되묻기 기능 정상 작동")
        print(f"  메시지: {result['clarification']['message']}")
        for option in result['clarification']['options']:
            print(f"  - {option['label']}")
    else:
        print("  되묻기 기능 오류")

def test_single_stock_performance():
    """단일 종목 성과 테스트"""
    print("\n단일 종목 성과 테스트")
    
    from agents.decisionmaker.ambiguous_agent import AmbiguousAgent
    
    agent = AmbiguousAgent(test_mode=True)  # 테스트 모드로 빠른 실행
    
    # 삼성전자 테스트
    symbol = "005930.KS"
    
    print(f"\n{symbol} 최근 성과:")
    
    # 최근 성과 계산
    performance = agent._calculate_recent_performance(symbol, 10)
    if performance:
        print(f"  최근 10일 성과: {performance['performance']}%")
        print(f"  현재가: {performance['recent_price']:,.0f}원")
        print(f"  10일 전: {performance['past_price']:,.0f}원")
    else:
        print("  성과 계산 실패")
    
    # 고점 대비 하락률 계산
    drop_data = agent._calculate_peak_drop(symbol, 252)
    if drop_data:
        print(f"  52주 고점 대비: {drop_data['drop_ratio']}%")
        print(f"  현재가: {drop_data['current_price']:,.0f}원")
        print(f"  고점: {drop_data['peak_price']:,.0f}원")
    else:
        print("  고점 대비 하락률 계산 실패")

def main():
    """메인 테스트 실행"""
    print("=" * 60)
    print("Task 4: 모호한 의미 해석 테스트")
    print("=" * 60)
    
    test_ambiguous_agent()
    test_single_stock_performance()
    
    print("\n" + "=" * 60)
    print("Task 4 테스트 완료")
    print("구현된 기능:")
    print("  - 최근 성과 계산 (수익률)")
    print("  - 고점 대비 하락률 계산")
    print("  - 되묻기 기능")
    print("  - 캐시 시스템")
    print("  - 정량화 로직")
    print("=" * 60)

if __name__ == "__main__":
    main() 