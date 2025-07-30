import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
import hashlib

class CacheManager:
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """캐시 디렉토리가 없으면 생성"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _get_cache_key(self, data_type: str, symbol: str, date: str, **kwargs) -> str:
        """캐시 키 생성"""
        key_data = {
            "type": data_type,
            "symbol": symbol,
            "date": date,
            **kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> str:
        """캐시 파일 경로 반환"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def get(self, data_type: str, symbol: str, date: str, max_age_hours: int = 24, **kwargs) -> Optional[Any]:
        """캐시에서 데이터 조회"""
        cache_key = self._get_cache_key(data_type, symbol, date, **kwargs)
        cache_path = self._get_cache_path(cache_key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 캐시 만료 확인
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cached_time > timedelta(hours=max_age_hours):
                os.remove(cache_path)  # 만료된 캐시 삭제
                return None
            
            return cache_data['data']
        
        except Exception:
            return None
    
    def set(self, data_type: str, symbol: str, date: str, data: Any, **kwargs):
        """캐시에 데이터 저장"""
        cache_key = self._get_cache_key(data_type, symbol, date, **kwargs)
        cache_path = self._get_cache_path(cache_key)
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"캐시 저장 실패: {e}")
    
    def clear_expired(self, max_age_hours: int = 24):
        """만료된 캐시 파일들 삭제"""
        if not os.path.exists(self.cache_dir):
            return
        
        current_time = datetime.now()
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.cache_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    cached_time = datetime.fromisoformat(cache_data['timestamp'])
                    if current_time - cached_time > timedelta(hours=max_age_hours):
                        os.remove(file_path)
                        print(f"만료된 캐시 삭제: {filename}")
                
                except Exception:
                    # 손상된 캐시 파일 삭제
                    try:
                        os.remove(file_path)
                    except:
                        pass 