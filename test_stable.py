#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.decisionmaker.screener_agent import ScreeningAgent
import time

def test_stable_screener():
    """안정적인 스크리너 테스트"""
    print("=== 안정적인 스크리너 테스트 ===")
    
    screener = ScreeningAgent()
    
    # 간단한 테스트 쿼리
    test_query = {
        "date": "2024-01-15",
        "condition": {
            "volume_change": "30%",
            "volume_direction": "up"
        },
        "limit": 3
    }
    
    print(f"테스트 쿼리: {test_query}")
    
    start_time = time.time()
    result = screener.handle(test_query)
    end_time = time.time()
    
    print(f"소요시간: {end_time - start_time:.2f}초")
    
    if 'error' in result:
        print(f"❌ 오류: {result['error']}")
    else:
        print(f"✅ 성공!")
        print(f"찾은 종목 수: {len(result.get('judgment', []))}")
        print(f"요약: {result.get('judgment_summary')}")
        
        # 결과 출력
        for item in result.get('judgment', []):
            print(f"- {item['name']} ({item['code']}): {item['change_ratio']}%")
    
    print("\n🎉 테스트 완료!")

if __name__ == "__main__":
    test_stable_screener() 