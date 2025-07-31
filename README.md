# Financial Multi-Agent System (MAS)

A **modular multi-agent system** designed for **financial market analysis** and **decision-making** using Python.

This repository contains a system where **each agent is responsible for a distinct stage in the investment workflow** — from **data collection** to **signal generation** — with communication managed through an **orchestrator** and a **shared event bus**. The architecture promotes modularity, scalability, and explainability, making it ideal for experimental finance automation.

---


## Project Structure
```
financial_mas/
├── main.py                             # Entry point for orchestrated agent execution
├── test_integrated.py                  # Basic test for orchestrator and agents
├── .env                                # Environment variables (e.g., CLOVA_API_KEY)
├── README.md                           # You're here
│
├── agents/
│   ├── base_agent.py                    # 공통 Agent 추상화 클래스
│   ├── orchestrator.py                  # 멀티에이전트 파이프라인 관리자
│   │
│   ├── interpreter/                     # 질의 해석 레이어
│   │   ├── symbol_resolver_agent.py     # 종목명 ↔ 코드 매핑 (KOSPI/KOSDAQ)
│   │   └── query_understander_agent.py  # 의도 분석, 날짜·조건 구조화
│   │
│   ├── decisionmaker/                   # 의사결정 레이어
│   │   ├── analyzer_agent.py            # 단순 조회, 수치 계산
│   │   ├── screener_agent.py            # 조건 검색
│   │   ├── signal_agent.py              # 기술적 신호 감지 (RSI, 이동평균 등)
│   │   ├── advanced_agent.py            # 상관관계, 변동성, 모멘텀 분석
│   │   └── ambiguous_agent.py           # 모호한 질의 명확화
│   │
│   └── responder/
│       └── summarizer_agent.py          # HyperCLOVA-X 기반 자연어 응답 생성
│
├── data/
│   ├── krx_stocks.csv                   # 한국거래소 종목 데이터
│   └── yfinance_data.py                 # Yahoo Finance 데이터 처리
│
└── api/
    ├── yfinance_api.py                  # Yahoo Finance API 인터페이스
    └── hyperclova_api.py                # HyperCLOVA-X API 인터페이스
```

---

##  Key Features

### 1. Interpreter Layer
사용자 질의 전처리 및 구조화

자연어 질의를 금융 도메인에 맞게 파싱
종목명 추출 및 표준화
날짜 인식 및 정규화
사용자 의도(intent) 분류

### 2. DecisionMaker Layer
데이터 기반 의사결정 및 분석

analyzer_agent: 기본적인 주가 조회 및 수치 계산  

screener_agent: 조건부 종목 검색 및 필터링  

signal_agent: RSI, 이동평균 등 기술적 지표 분석  

advanced_agent: 상관관계, 변동성, 모멘텀 등 고급 분석  

ambiguous_agent: 모호한 질의에 대한 명확화 요청

### 3. Responder Layer
분석 결과의 자연어 변환

구조화된 분석 결과를 사용자 친화적 형태로 변환
HyperCLOVA-X를 활용한 유연한 커뮤니케이션
컨텍스트 기반 응답 최적화

### 4. Orchestrator
파이프라인 조율 및 관리

Interpreter → DecisionMaker → Responder 흐름 관리
사용자 의도에 따른 적절한 Agent 선택 및 호출
병렬 처리 및 성능 최적화

### 5. 설계 원칙
모듈화 및 확장성

역할 기반 분리: 각 레이어는 명확한 단일 책임을 가짐  

인터페이스 통일: 모든 Agent는 context(dict)를 입출력으로 사용  

병렬 처리 지원: DecisionMaker 레이어의 Agent들은 독립적으로 실행 가능

---

##  Architecture Diagram
<img width="3840" height="3710" alt="Image" src="https://github.com/user-attachments/assets/86708e67-7537-4a1e-96a6-1d2995fa0847" />

---

##  Getting Started

### 1. Clone the Repository

```bash
git clone -b dh https://github.com/annoeyed/financial_mas.git
cd financial_mas
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

Create a .env file in the root directory and add your API keys:

``` ini
CLOVA_API_KEY=your_key_here
```

### 4. Run the System
``` bash
python main.py
```

### Run Test
``` bash
python test_integrated.py
```

### Dependencies
``` cpp
numpy==2.3.2
pandas==2.3.1
python-dotenv==1.1.1
python_dateutil==2.9.0.post0
PyYAML==6.0.2
PyYAML==6.0.2
Requests==2.32.4
yfinance==0.2.65

```
Check requirements.txt for the complete list.

---
## License
This project is for educational and research purposes only.

---
## Authors
- **Nayeon Kim** [@annoeyed](https://github.com/annoeyed)  
- **Donghee Kim** [@donghee290](https://github.com/donghee290)  
- **Jimin Hwang** [@specture258](https://github.com/specture258)  
---
