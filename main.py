#!/usr/bin/env python3
"""
금융 멀티에이전트 시스템 메인 엔트리포인트
사용자 질의를 받아 멀티에이전트 파이프라인을 통해 처리하고 응답을 반환합니다.
"""

import asyncio
import sys
import time
import json
from typing import Dict, Any, Optional
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(str(Path(__file__).parent))

from agents.orchestrator import Orchestrator
from utils.logger import logger


class FinancialAgentSystem:
    """금융 멀티에이전트 시스템 메인 클래스"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        시스템 초기화
        :param config_path: 설정 파일 경로 (선택사항)
        """
        self.orchestrator = Orchestrator(config_path)
        self.session_history = []
        self.start_time = time.time()
        
        logger.info("금융 멀티에이전트 시스템이 초기화되었습니다.")
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """
        사용자 질의를 처리하는 메인 메서드
        :param query: 사용자 질의
        :return: 처리 결과
        """
        if not query.strip():
            return {
                "error": "질문이 입력되지 않았습니다.",
                "response": "질문을 입력해주세요."
            }
        
        start_time = time.time()
        logger.info(f"질의 처리 시작: {query[:50]}...")
        
        try:
            # Orchestrator를 통해 파이프라인 실행
            result = await self.orchestrator.async_run(query)
            
            # 처리 시간 계산
            processing_time = time.time() - start_time
            
            # 세션 히스토리에 기록
            session_entry = {
                "query": query,
                "result": result,
                "processing_time": processing_time,
                "timestamp": time.time()
            }
            self.session_history.append(session_entry)
            
            # 결과에 메타데이터 추가
            result["processing_time"] = processing_time
            result["session_id"] = len(self.session_history)
            
            logger.info(f"질의 처리 완료 (소요시간: {processing_time:.2f}초)")
            return result
            
        except Exception as e:
            logger.error(f"질의 처리 중 오류 발생: {e}")
            return {
                "error": str(e),
                "query": query,
                "processing_time": time.time() - start_time
            }
    
    def run_sync(self, query: str) -> Dict[str, Any]:
        """
        동기 방식으로 질의 처리
        :param query: 사용자 질의
        :return: 처리 결과
        """
        return asyncio.run(self.process_query(query))
    
    def get_session_stats(self) -> Dict[str, Any]:
        """세션 통계 정보 반환"""
        if not self.session_history:
            return {"total_queries": 0, "avg_processing_time": 0}
        
        total_queries = len(self.session_history)
        avg_processing_time = sum(
            entry["processing_time"] for entry in self.session_history
        ) / total_queries
        
        return {
            "total_queries": total_queries,
            "avg_processing_time": avg_processing_time,
            "system_uptime": time.time() - self.start_time
        }
    
    def clear_history(self):
        """세션 히스토리 초기화"""
        self.session_history.clear()
        logger.info("세션 히스토리가 초기화되었습니다.")


def print_response(result: Dict[str, Any], show_details: bool = False):
    """
    응답 결과를 포맷팅하여 출력
    :param result: 처리 결과
    :param show_details: 상세 정보 표시 여부
    """
    print("\n" + "="*60)
    print("금융 멀티에이전트 시스템 응답")
    print("="*60)
    
    if "error" in result:
        print(f"오류: {result['error']}")
        return
    
    # 주요 응답 출력
    if "response" in result:
        print(f"응답: {result['response']}")
    
    # 처리 시간 표시
    if "processing_time" in result:
        print(f"처리 시간: {result['processing_time']:.2f}초")
    
    # 상세 정보 표시 (디버그 모드)
    if show_details and "intermediate" in result:
        print("\n상세 처리 정보:")
        for agent_name, agent_result in result["intermediate"].items():
            if agent_result:
                print(f"  - {agent_name}: {str(agent_result)[:100]}...")
    
    # 의도 분석 결과 표시
    if "intent" in result and result["intent"]:
        print(f"\n분석된 의도: {result['intent']}")
    
    print("="*60)


def interactive_mode():
    """대화형 모드 실행"""
    system = FinancialAgentSystem()
    
    print("금융 멀티에이전트 시스템에 오신 것을 환영합니다!")
    print("도움말:")
    print("  - 질문을 입력하세요 (예: '삼성전자 주가 알려줘')")
    print("  - 'quit' 또는 'exit'로 종료")
    print("  - 'stats'로 세션 통계 확인")
    print("  - 'clear'로 히스토리 초기화")
    print("  - 'debug'로 상세 모드 전환")
    print("-" * 60)
    
    debug_mode = False
    
    while True:
        try:
            user_input = input("\n질문을 입력하세요: ").strip()
            
            if not user_input:
                continue
            
            # 특별 명령어 처리
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("시스템을 종료합니다. 감사합니다!")
                break
            
            elif user_input.lower() == 'stats':
                stats = system.get_session_stats()
                print(f"\n세션 통계:")
                print(f"  - 총 질의 수: {stats['total_queries']}")
                print(f"  - 평균 처리 시간: {stats['avg_processing_time']:.2f}초")
                print(f"  - 시스템 가동 시간: {stats['system_uptime']:.1f}초")
                continue
            
            elif user_input.lower() == 'clear':
                system.clear_history()
                print("히스토리가 초기화되었습니다.")
                continue
            
            elif user_input.lower() == 'debug':
                debug_mode = not debug_mode
                print(f"디버그 모드: {'켜짐' if debug_mode else '꺼짐'}")
                continue
            
            # 일반 질의 처리
            result = system.run_sync(user_input)
            print_response(result, show_details=debug_mode)
            
        except KeyboardInterrupt:
            print("\n\n시스템을 종료합니다. 감사합니다!")
            break
        except Exception as e:
            logger.error(f"대화형 모드에서 오류 발생: {e}")
            print(f"오류가 발생했습니다: {e}")


def batch_mode(queries: list):
    """
    배치 모드로 여러 질의를 처리
    :param queries: 처리할 질의 리스트
    """
    system = FinancialAgentSystem()
    results = []
    
    print(f"배치 모드: {len(queries)}개 질의 처리 시작")
    
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] 처리 중: {query[:50]}...")
        result = system.run_sync(query)
        results.append(result)
        
        if "error" in result:
            print(f"오류: {result['error']}")
        else:
            response = result.get('response', '응답 없음')
            if isinstance(response, dict):
                response = response.get('response', str(response))
            print(f"응답: {response[:100]}...")
            print(f"완료 (소요시간: {result.get('processing_time', 0):.2f}초)")
    
    # 배치 처리 결과 요약
    successful = sum(1 for r in results if "error" not in r)
    total_time = sum(r.get("processing_time", 0) for r in results)
    
    print(f"\n배치 처리 완료:")
    print(f"  - 성공: {successful}/{len(queries)}")
    print(f"  - 총 소요시간: {total_time:.2f}초")
    print(f"  - 평균 처리시간: {total_time/len(queries):.2f}초")


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="금융 멀티에이전트 시스템")
    parser.add_argument("--query", "-q", help="처리할 질의")
    parser.add_argument("--batch", "-b", help="배치 처리할 질의 파일 (JSON)")
    parser.add_argument("--config", "-c", help="설정 파일 경로")
    parser.add_argument("--debug", "-d", action="store_true", help="디버그 모드")
    
    args = parser.parse_args()
    
    # 로깅 레벨 설정
    if args.debug:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        if args.batch:
            # 배치 모드
            with open(args.batch, 'r', encoding='utf-8') as f:
                queries = json.load(f)
            batch_mode(queries)
        
        elif args.query:
            # 단일 질의 모드
            system = FinancialAgentSystem(args.config)
            result = system.run_sync(args.query)
            print_response(result, show_details=args.debug)
        
        else:
            # 대화형 모드
            interactive_mode()
    
    except KeyboardInterrupt:
        print("\n시스템을 종료합니다.")
    except Exception as e:
        logger.error(f"시스템 실행 중 오류 발생: {e}")
        print(f"시스템 오류: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()