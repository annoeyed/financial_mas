#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.yfinance_api import get_volume_data, get_bulk_volume_parallel
import time

def test_simple():
    """간단한 테스트"""
    print("=== 간단한 API 테스트 ===")
    
    # 대형주 5개만 테스트
    symbols = [
        "005930.KS",  # 삼성전자
        "000660.KS",  # SK하이닉스
        "035420.KS",  # NAVER
        "051910.KS",  # LG화학
        "006400.KS"   # 삼성SDI
    ]
    
    test_date = "2024-01-15"
    
    print(f"테스트 종목: {len(symbols)}개")
    print(f"테스트 날짜: {test_date}")
    
    start_time = time.time()
    result = get_bulk_volume_parallel(symbols, test_date, workers=2)
    end_time = time.time()
    
    print(f"성공한 종목 수: {len(result)}")
    print(f"소요시간: {end_time - start_time:.2f}초")
    
    for symbol, volume in result.items():
        print(f"{symbol}: {volume:,}")
    
    print("\n 테스트 완료!")

if __name__ == "__main__":
    test_simple() 