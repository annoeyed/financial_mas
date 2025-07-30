#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

def test_symbol_formats():
    """다양한 심볼 형식 테스트"""
    print("=== 한국 주식 심볼 형식 테스트 ===")
    
    # 다양한 심볼 형식들
    symbol_formats = [
        "005930.KS",      # 기존 형식
        "005930.KRX",     # KRX 형식
        "005930",         # 심볼만
        "005930.KS",      # 다시 기존
    ]
    
    test_date = "2024-01-15"
    
    for symbol in symbol_formats:
        print(f"\n테스트 심볼: {symbol}")
        
        try:
            # 기본 데이터 다운로드
            start_time = time.time()
            df = yf.download(symbol, start="2024-01-01", end="2024-01-20", progress=False)
            end_time = time.time()
            
            if not df.empty:
                print(f"✅ 성공! 데이터 행 수: {len(df)}")
                print(f"  컬럼: {list(df.columns)}")
                print(f"  첫 번째 데이터: {df.iloc[0] if len(df) > 0 else 'None'}")
                print(f"  소요시간: {end_time - start_time:.2f}초")
                
                # 이동평균 계산 시도
                if len(df) >= 50:
                    df['MA50'] = df['Close'].rolling(window=50).mean()
                    latest_ma = df['MA50'].iloc[-1]
                    latest_price = df['Close'].iloc[-1]
                    
                    if pd.notna(latest_ma) and pd.notna(latest_price):
                        breakout_ratio = ((latest_price - latest_ma) / latest_ma) * 100
                        print(f"  이동평균 계산 성공!")
                        print(f"  현재가: {latest_price:,.2f}원")
                        print(f"  50일 이동평균: {latest_ma:,.2f}원")
                        print(f"  돌파율: {breakout_ratio:.2f}%")
                        break
                    else:
                        print(f"  ❌ 이동평균 계산 실패 (데이터 부족)")
                else:
                    print(f"  ❌ 데이터 부족 (50일 이동평균 계산 불가)")
            else:
                print(f"❌ 데이터 없음")
                
        except Exception as e:
            print(f"❌ 오류: {e}")

def test_simple_price():
    """간단한 가격 조회 테스트"""
    print("\n=== 간단한 가격 조회 테스트 ===")
    
    symbol = "005930.KS"
    
    try:
        ticker = yf.Ticker(symbol)
        
        # 현재 정보
        info = ticker.info
        print(f"종목명: {info.get('longName', 'Unknown')}")
        print(f"현재가: {info.get('currentPrice', 'Unknown')}")
        print(f"시가총액: {info.get('marketCap', 'Unknown')}")
        
        # 히스토리 데이터
        hist = ticker.history(period="5d")
        if not hist.empty:
            print(f"최근 5일 데이터: {len(hist)}행")
            print(f"최신 종가: {hist['Close'].iloc[-1]:,.2f}원")
        else:
            print("히스토리 데이터 없음")
            
    except Exception as e:
        print(f"오류: {e}")

def test_alternative_symbols():
    """대안 심볼들 테스트"""
    print("\n=== 대안 심볼들 테스트 ===")
    
    # 다른 대형주들 테스트
    test_symbols = [
        "000660.KS",  # SK하이닉스
        "035420.KS",  # NAVER
        "051910.KS",  # LG화학
    ]
    
    for symbol in test_symbols:
        print(f"\n테스트: {symbol}")
        
        try:
            df = yf.download(symbol, start="2024-01-01", end="2024-01-20", progress=False)
            
            if not df.empty:
                print(f"✅ 성공! {len(df)}행 데이터")
                latest_price = df['Close'].iloc[-1]
                print(f"  최신 종가: {latest_price:,.2f}원")
            else:
                print(f"❌ 데이터 없음")
                
        except Exception as e:
            print(f"❌ 오류: {e}")

if __name__ == "__main__":
    test_symbol_formats()
    test_simple_price()
    test_alternative_symbols() 