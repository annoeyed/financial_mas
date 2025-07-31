#!/usr/bin/env python3
"""
FastAPI 서버 - 금융 멀티에이전트 시스템 API
"""

import asyncio
import sys
import time
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from pydantic import BaseModel, Field

# FastAPI 관련 import
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(str(Path(__file__).parent))

from agents.orchestrator import Orchestrator
from utils.logger import logger

# Pydantic 모델 정의
class QueryRequest(BaseModel):
    query: str = Field(..., description="사용자 질의", min_length=1, max_length=1000)
    session_id: Optional[str] = Field(None, description="세션 ID")

class QueryResponse(BaseModel):
    success: bool = Field(..., description="처리 성공 여부")
    response: Dict[str, Any] = Field(..., description="응답 데이터")
    processing_time: float = Field(..., description="처리 시간(초)")
    session_id: Optional[str] = Field(None, description="세션 ID")

class HealthResponse(BaseModel):
    status: str = Field(..., description="서버 상태")
    uptime: float = Field(..., description="서버 가동 시간(초)")
    total_queries: int = Field(..., description="총 처리된 질의 수")

# FastAPI 앱 생성
app = FastAPI(
    title="금융 멀티에이전트 시스템 API",
    description="금융 관련 질의를 처리하는 멀티에이전트 시스템 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 변수
financial_system = None
start_time = time.time()

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """서버 시작/종료 시 이벤트 처리"""
    global financial_system
    try:
        financial_system = Orchestrator()
        logger.info("FastAPI 서버가 시작되었습니다.")
        yield
    except Exception as e:
        logger.error(f"서버 초기화 중 오류 발생: {e}")
        raise
    finally:
        logger.info("FastAPI 서버가 종료되었습니다.")

# FastAPI 앱 생성 (lifespan 이벤트 추가)
app = FastAPI(
    title="금융 멀티에이전트 시스템 API",
    description="금융 관련 질의를 처리하는 멀티에이전트 시스템 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

@app.get("/", response_model=Dict[str, str])
async def root():
    """루트 엔드포인트"""
    return {
        "message": "금융 멀티에이전트 시스템 API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """헬스 체크 엔드포인트"""
    global financial_system, start_time
    
    if financial_system is None:
        raise HTTPException(status_code=503, detail="서버가 초기화되지 않았습니다.")
    
    uptime = time.time() - start_time
    
    return HealthResponse(
        status="healthy",
        uptime=uptime,
        total_queries=0  # TODO: 실제 통계 구현
    )

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """사용자 질의 처리 엔드포인트"""
    global financial_system
    
    if financial_system is None:
        raise HTTPException(status_code=503, detail="서버가 초기화되지 않았습니다.")
    
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="질문이 입력되지 않았습니다.")
    
    start_time = time.time()
    
    try:
        # 질의 처리
        result = await financial_system.async_run(request.query)
        
        processing_time = time.time() - start_time
        
        return QueryResponse(
            success=True,
            response=result,
            processing_time=processing_time,
            session_id=request.session_id
        )
        
    except Exception as e:
        logger.error(f"질의 처리 중 오류 발생: {e}")
        processing_time = time.time() - start_time
        
        return QueryResponse(
            success=False,
            response={
                "error": str(e),
                "query": request.query
            },
            processing_time=processing_time,
            session_id=request.session_id
        )

@app.post("/query/sync", response_model=QueryResponse)
async def process_query_sync(request: QueryRequest):
    """동기 방식 질의 처리 엔드포인트"""
    global financial_system
    
    if financial_system is None:
        raise HTTPException(status_code=503, detail="서버가 초기화되지 않았습니다.")
    
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="질문이 입력되지 않았습니다.")
    
    start_time = time.time()
    
    try:
        # 동기 방식으로 질의 처리
        result = financial_system.run(request.query)
        
        processing_time = time.time() - start_time
        
        return QueryResponse(
            success=True,
            response=result,
            processing_time=processing_time,
            session_id=request.session_id
        )
        
    except Exception as e:
        logger.error(f"질의 처리 중 오류 발생: {e}")
        processing_time = time.time() - start_time
        
        return QueryResponse(
            success=False,
            response={
                "error": str(e),
                "query": request.query
            },
            processing_time=processing_time,
            session_id=request.session_id
        )

@app.get("/stats", response_model=Dict[str, Any])
async def get_stats():
    """시스템 통계 정보 반환"""
    global financial_system, start_time
    
    if financial_system is None:
        raise HTTPException(status_code=503, detail="서버가 초기화되지 않았습니다.")
    
    uptime = time.time() - start_time
    
    return {
        "uptime": uptime,
        "status": "running",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    # 개발 서버 실행
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 