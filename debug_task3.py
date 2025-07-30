#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.yfinance_api import get_moving_average_data, get_bulk_moving_average_parallel
import time

def debug_single_vs_bulk():
    """단일 함수 vs 병렬 함수 비교"""
    print("=== 디버그: 단일 vs 병렬 함수 비교 ===")
    
    symbol = "005930.KS"
    test_date = "2024-01-15"
    
    print(f"테스트 종목: {symbol}")
    print(f"테스트 날짜: {test_date}")
    
    # 1. 단일 함수 테스트
    print("\n1. 단일 함수 테스트:")
    start_time = time.time()
    ma_data_single = get_moving_average_data(symbol, test_date, period=50)
    time_single = time.time() - start_time
    
    if ma_data_single:
        print(f"✅ 성공: {ma_data_single}")
    else:
        print(f"❌ 실패")
    print(f"소요시간: {time_single:.2f}초")
    
    # 2. 병렬 함수 테스트
    print("\n2. 병렬 함수 테스트:")
    start_time = time.time()
    ma_data_map = get_bulk_moving_average_parallel([symbol], test_date, period=50, workers=1)
    time_bulk = time.time() - start_time
    
    ma_data_bulk = ma_data_map.get(symbol)
    if ma_data_bulk:
        print(f"✅ 성공: {ma_data_bulk}")
    else:
        print(f"❌ 실패")
    print(f"소요시간: {time_bulk:.2f}초")
    
    # 3. 결과 비교
    print("\n3. 결과 비교:")
    if ma_data_single and ma_data_bulk:
        print("✅ 둘 다 성공")
        print(f"단일: {ma_data_single['current_price']} vs 병렬: {ma_data_bulk['current_price']}")
    elif ma_data_single and not ma_data_bulk:
        print("❌ 단일만 성공")
    elif not ma_data_single and ma_data_bulk:
        print("❌ 병렬만 성공")
    else:
        print("❌ 둘 다 실패")

def debug_with_different_dates():
    """다른 날짜로 테스트"""
    print("\n=== 다른 날짜로 테스트 ===")
    
    symbol = "005930.KS"
    test_dates = ["2024-01-15", "2024-01-10", "2024-01-05", "2024-12-15"]
    
    for test_date in test_dates:
        print(f"\n날짜: {test_date}")
        
        # 병렬 함수로 테스트
        ma_data_map = get_bulk_moving_average_parallel([symbol], test_date, period=50, workers=1)
        ma_data = ma_data_map.get(symbol)
        
        if ma_data:
            print(f"✅ 성공: 현재가 {ma_data['current_price']:,}원, 돌파율 {ma_data['breakout_ratio']}%")
            break
        else:
            print(f"❌ 실패")

def debug_signal_agent_style():
    """시그널 에이전트 스타일로 테스트"""
    print("\n=== 시그널 에이전트 스타일 테스트 ===")
    
    symbols = ["005930.KS", "000660.KS", "035420.KS"]
    test_date = "2024-01-15"
    
    print(f"테스트 종목: {symbols}")
    print(f"테스트 날짜: {test_date}")
    
    start_time = time.time()
    ma_data_map = get_bulk_moving_average_parallel(symbols, test_date, period=50, workers=3)
    end_time = time.time()
    
    print(f"성공한 종목 수: {len(ma_data_map)}")
    print(f"소요시간: {end_time - start_time:.2f}초")
    
    for symbol, data in ma_data_map.items():
        print(f"  {symbol}: 현재가 {data['current_price']:,}원, 돌파율 {data['breakout_ratio']}%")

if __name__ == "__main__":
    debug_single_vs_bulk()
    debug_with_different_dates()
    debug_signal_agent_style() 