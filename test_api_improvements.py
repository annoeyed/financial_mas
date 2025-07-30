#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.yfinance_api import get_volume_data, get_bulk_volume_parallel, get_rsi_data
from agents.decisionmaker.screener_agent import ScreeningAgent
import time
from datetime import datetime, timedelta

def test_single_api_call():
    """단일 API 호출 테스트"""
    print("=== 단일 API 호출 테스트 ===")
    
    symbol = "005930.KS"  # 삼성전자
    test_date = "2024-01-15"
    
    print(f"테스트 종목: {symbol}")
    print(f"테스트 날짜: {test_date}")
    
    start_time = time.time()
    volume = get_volume_data(symbol, test_date)
    end_time = time.time()
    
    print(f"거래량: {volume}")
    print(f"소요시간: {end_time - start_time:.2f}초")
    print()

def test_bulk_api_call():
    """대량 API 호출 테스트"""
    print("=== 대량 API 호출 테스트 ===")
    
    # 테스트용 종목들 (상위 10개)
    symbols = [
        "005930.KS",  # 삼성전자
        "000660.KS",  # SK하이닉스
        "035420.KS",  # NAVER
        "051910.KS",  # LG화학
        "006400.KS",  # 삼성SDI
        "035720.KS",  # 카카오
        "207940.KS",  # 삼성바이오로직스
        "068270.KS",  # 셀트리온
        "323410.KS",  # 카카오뱅크
        "051900.KS"   # LG생활건강
    ]
    
    test_date = "2024-01-15"
    
    print(f"테스트 종목 수: {len(symbols)}")
    print(f"테스트 날짜: {test_date}")
    
    start_time = time.time()
    result = get_bulk_volume_parallel(symbols, test_date, workers=5)
    end_time = time.time()
    
    print(f"성공한 종목 수: {len(result)}")
    print(f"소요시간: {end_time - start_time:.2f}초")
    print(f"초당 처리 종목 수: {len(result)/(end_time - start_time):.2f}")
    print()
    
    # 결과 일부 출력
    for i, (symbol, volume) in enumerate(list(result.items())[:5]):
        print(f"{symbol}: {volume:,}")

def test_screener_agent():
    """스크리너 에이전트 테스트"""
    print("=== 스크리너 에이전트 테스트 ===")
    
    screener = ScreeningAgent()
    
    # 테스트 쿼리
    test_query = {
        "date": "2024-01-15",
        "condition": {
            "volume_change": "50%",
            "volume_direction": "up"
        },
        "limit": 5
    }
    
    print(f"테스트 쿼리: {test_query}")
    
    start_time = time.time()
    result = screener.handle(test_query)
    end_time = time.time()
    
    print(f"소요시간: {end_time - start_time:.2f}초")
    print(f"결과 타입: {result.get('judgment_type')}")
    
    if 'error' in result:
        print(f"오류: {result['error']}")
    else:
        print(f"찾은 종목 수: {len(result.get('judgment', []))}")
        print(f"요약: {result.get('judgment_summary')}")
        
        # 결과 일부 출력
        for item in result.get('judgment', [])[:3]:
            print(f"- {item['name']} ({item['code']}): {item['change_ratio']}%")

def test_cache_functionality():
    """캐시 기능 테스트"""
    print("=== 캐시 기능 테스트 ===")
    
    symbol = "005930.KS"
    test_date = "2024-01-15"
    
    print(f"첫 번째 호출 (API 사용)")
    start_time = time.time()
    volume1 = get_volume_data(symbol, test_date)
    time1 = time.time() - start_time
    print(f"거래량: {volume1}, 소요시간: {time1:.3f}초")
    
    print(f"두 번째 호출 (캐시 사용)")
    start_time = time.time()
    volume2 = get_volume_data(symbol, test_date)
    time2 = time.time() - start_time
    print(f"거래량: {volume2}, 소요시간: {time2:.3f}초")
    
    if volume1 == volume2:
        print("캐시 기능 정상 작동")
        if time2 > 0:
            print(f"속도 향상: {time1/time2:.1f}배")
        else:
            print("속도 향상: 거의 즉시 (캐시 효과)")
    else:
        print("캐시 기능 오류")

def main():
    """메인 테스트 함수"""
    print("API 개선사항 테스트 시작\n")
    
    try:
        # 1. 단일 API 호출 테스트
        test_single_api_call()
        
        # 2. 캐시 기능 테스트
        test_cache_functionality()
        
        # 3. 대량 API 호출 테스트
        test_bulk_api_call()
        
        # 4. 스크리너 에이전트 테스트 (선택적)
        print("스크리너 에이전트 테스트를 실행하시겠습니까? (시간이 오래 걸릴 수 있습니다)")
        response = input("실행하려면 'y'를 입력하세요: ")
        if response.lower() == 'y':
            test_screener_agent()
        
        print("\n모든 테스트 완료!")
        
    except Exception as e:
        print(f"테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 