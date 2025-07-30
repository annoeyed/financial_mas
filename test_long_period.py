#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

def test_long_period_data():
    """긴 기간 데이터 테스트"""
    print("=== 긴 기간 데이터 테스트 ===")
    
    symbol = "005930.KS"
    
    # 2023년 전체 데이터 가져오기
    start_date = "2023-01-01"
    end_date = "2024-01-20"
    
    print(f"심볼: {symbol}")
    print(f"기간: {start_date} ~ {end_date}")
    
    start_time = time.time()
    df = yf.download(symbol, start=start_date, end=end_date, auto_adjust=False, progress=False, threads=False)
    end_time = time.time()
    
    print(f"소요시간: {end_time - start_time:.2f}초")
    print(f"데이터 행 수: {len(df)}")
    
    if not df.empty:
        print(f"데이터 범위: {df.index[0].date()} ~ {df.index[-1].date()}")
        print(f"컬럼: {list(df.columns)}")
        
        # 50일 이동평균 계산
        if len(df) >= 50:
            df['MA50'] = df['Close'].rolling(window=50).mean()
            
            # 2024-01-15 근처 데이터 확인
            target_date = pd.to_datetime("2024-01-15").date()
            
            for idx, row in df.iterrows():
                if idx.date() >= target_date:
                    current_price = row['Close'].item()
                    ma50 = row['MA50'].item()
                    
                    if pd.notna(ma50):
                        breakout_ratio = ((current_price - ma50) / ma50) * 100
                        
                        print(f"\n 이동평균 계산 성공!")
                        print(f"날짜: {idx.date()}")
                        print(f"현재가: {current_price:,.2f}원")
                        print(f"50일 이동평균: {ma50:,.2f}원")
                        print(f"돌파율: {breakout_ratio:.2f}%")
                        print(f"돌파 여부: {'예' if breakout_ratio > 10 else '아니오'}")
                        break
                    else:
                        print(f" 이동평균 계산 실패 (데이터 부족)")
                        break
            else:
                print(f" 해당 날짜 데이터 없음")
        else:
            print(f" 데이터 부족 (50일 이동평균 계산 불가)")
    else:
        print(f" 데이터 없음")

def test_updated_moving_average():
    """수정된 이동평균 함수 테스트"""
    print("\n=== 수정된 이동평균 함수 테스트 ===")
    
    from api.yfinance_api import get_moving_average_data
    
    symbol = "005930.KS"
    test_date = "2024-01-15"
    
    print(f"심볼: {symbol}")
    print(f"날짜: {test_date}")
    
    start_time = time.time()
    ma_data = get_moving_average_data(symbol, test_date, period=50)
    end_time = time.time()
    
    if ma_data:
        print(f" 성공!")
        print(f"현재가: {ma_data['current_price']:,}원")
        print(f"50일 이동평균: {ma_data['moving_average']:,.2f}원")
        print(f"돌파율: {ma_data['breakout_ratio']}%")
        print(f"돌파 여부: {'예' if ma_data['is_breakout'] else '아니오'}")
        print(f"소요시간: {end_time - start_time:.2f}초")
    else:
        print(f" 실패 (소요시간: {end_time - start_time:.2f}초)")

if __name__ == "__main__":
    test_long_period_data()
    test_updated_moving_average() 