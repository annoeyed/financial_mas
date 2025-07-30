#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from datetime import datetime

def test_advanced_agent():
    """Task 5: 고급 분석 기능 테스트"""
    print("Task 5: 고급 분석 기능 테스트 시작")
    
    from agents.decisionmaker.advanced_agent import AdvancedAgent
    
    agent = AdvancedAgent(test_mode=True)  # 테스트 모드로 빠른 실행
    
    # 테스트 1: 상관관계 분석
    print("\n1. 상관관계 분석 테스트")
    query = {
        'type': 'correlation',
        'days': 60
    }
    
    try:
        start_time = time.time()
        result = agent.handle(query)
        end_time = time.time()
        
        if result['success']:
            print(f"  성공! {result['total_pairs']}개 높은 상관관계 쌍 발견")
            for pair in result['high_correlation_pairs'][:3]:  # 상위 3개만 출력
                print(f"  - {pair['symbol1']} ↔ {pair['symbol2']}: {pair['correlation']}")
            print(f"  소요시간: {end_time - start_time:.2f}초")
        else:
            print(f"  실패: {result.get('message', '알 수 없는 오류')}")
    except Exception as e:
        print(f"  상관관계 분석 오류: {e}")
    
    # 테스트 2: 변동성 분석
    print("\n2. 변동성 분석 테스트")
    query = {
        'type': 'volatility',
        'days': 60
    }
    
    try:
        start_time = time.time()
        result = agent.handle(query)
        end_time = time.time()
        
        if result['success']:
            print(f"  성공! {len(result['volatility_ranking'])}개 종목 분석")
            print(f"  고변동성 종목: {len(result['high_volatility'])}개")
            print(f"  저변동성 종목: {len(result['low_volatility'])}개")
            for stock in result['volatility_ranking'][:3]:  # 상위 3개만 출력
                print(f"  - {stock['symbol']}: {stock['volatility']}% 변동성")
            print(f"  소요시간: {end_time - start_time:.2f}초")
        else:
            print(f"  실패: {result.get('message', '알 수 없는 오류')}")
    except Exception as e:
        print(f"  변동성 분석 오류: {e}")
    
    # 테스트 3: 모멘텀 분석
    print("\n3. 모멘텀 분석 테스트")
    query = {
        'type': 'momentum',
        'periods': [5, 10, 20]
    }
    
    try:
        start_time = time.time()
        result = agent.handle(query)
        end_time = time.time()
        
        if result['success']:
            print(f"  성공! {len(result['momentum_ranking'])}개 종목 분석")
            print(f"  강한 모멘텀: {len(result['strong_momentum'])}개")
            print(f"  약한 모멘텀: {len(result['weak_momentum'])}개")
            for stock in result['momentum_ranking'][:3]:  # 상위 3개만 출력
                print(f"  - {stock['symbol']}: {stock['weighted_momentum']}% 모멘텀")
            print(f"  소요시간: {end_time - start_time:.2f}초")
        else:
            print(f"  실패: {result.get('message', '알 수 없는 오류')}")
    except Exception as e:
        print(f"  모멘텀 분석 오류: {e}")
    
    # 테스트 4: 포트폴리오 최적화
    print("\n4. 포트폴리오 최적화 테스트")
    query = {
        'type': 'portfolio',
        'target_return': 0.1
    }
    
    try:
        start_time = time.time()
        result = agent.handle(query)
        end_time = time.time()
        
        if result['success']:
            print(f"  성공! {result['total_analyzed']}개 종목 분석")
            print(f"  {result['recommendation']}")
            for stock in result['optimal_portfolio'][:3]:  # 상위 3개만 출력
                print(f"  - {stock['symbol']}: 수익률 {stock['return']}%, 변동성 {stock['volatility']}%, 샤프비율 {stock['sharpe_ratio']}")
            print(f"  소요시간: {end_time - start_time:.2f}초")
        else:
            print(f"  실패: {result.get('message', '알 수 없는 오류')}")
    except Exception as e:
        print(f"  포트폴리오 최적화 오류: {e}")

def test_single_analysis():
    """단일 종목 고급 분석 테스트"""
    print("\n단일 종목 고급 분석 테스트")
    
    from agents.decisionmaker.advanced_agent import AdvancedAgent
    
    agent = AdvancedAgent(test_mode=True)
    
    # 삼성전자 상세 분석
    symbol = "005930.KS"
    
    print(f"\n{symbol} 상세 분석:")
    
    # 변동성 분석
    df = agent._get_historical_data(symbol, 60)
    if df is not None:
        returns = df['Close'].pct_change().dropna()
        volatility = returns.std().item() * (252 ** 0.5) * 100
        
        print(f"  변동성: {volatility:.2f}%")
        print(f"  최고가: {df['High'].max().item():,.0f}원")
        print(f"  최저가: {df['Low'].min().item():,.0f}원")
        print(f"  현재가: {df['Close'].iloc[-1].item():,.0f}원")
        
        # 모멘텀 계산
        current_price = df['Close'].iloc[-1].item()
        momentum_5 = ((current_price - df['Close'].iloc[-5].item()) / df['Close'].iloc[-5].item()) * 100
        momentum_10 = ((current_price - df['Close'].iloc[-10].item()) / df['Close'].iloc[-10].item()) * 100
        
        print(f"  5일 모멘텀: {momentum_5:.2f}%")
        print(f"  10일 모멘텀: {momentum_10:.2f}%")

def main():
    """메인 테스트 실행"""
    print("=" * 60)
    print("Task 5: 고급 분석 기능 테스트")
    print("=" * 60)
    
    test_advanced_agent()
    test_single_analysis()
    
    print("\n" + "=" * 60)
    print("Task 5 테스트 완료")
    print("구현된 기능:")
    print("  - 상관관계 분석 (종목 간 관계)")
    print("  - 변동성 분석 (리스크 측정)")
    print("  - 모멘텀 분석 (가격 추세)")
    print("  - 포트폴리오 최적화 (샤프 비율)")
    print("  - 캐시 시스템 (성능 향상)")
    print("=" * 60)

if __name__ == "__main__":
    main() 