# Financial Multi-Agent System (MAS)

A **modular multi-agent system** designed for **financial market analysis** and **decision-making** using Python.

This repository contains a system where **each agent is responsible for a distinct stage in the investment workflow** — from **data collection** to **signal generation** — with communication managed through an **orchestrator** and a **shared event bus**. The architecture promotes modularity, scalability, and explainability, making it ideal for experimental finance automation.

---


## Project Structure
```
financial_mas/
│
├── core/ # Core agents and orchestrator logic
├── datapool/ # Data retrieval (e.g., YFinance, KIND)
├── messaging/ # Message passing and agent communication
├── utils/ # Utility functions
│
├── main.py # Entry point for orchestrated agent execution
├── test.py # Basic test for orchestrator and agents
├── .env # Environment variables (e.g., API keys)
└── README.md # You're here
```

---

##  Key Features

-  **Multi-Agent Architecture**: Role-specific agents handle stages like screening, scoring, and signal issuing
-  **Asynchronous Messaging**: Agents communicate via an event-driven shared message bus
-  **Integrated Data Sources**: Supports [YFinance](https://pypi.org/project/yfinance/), KIND, DART, and other APIs
-  **Signal Generation**: Agents produce simple buy/sell signals based on rules or ML logic
-  **Built-in Test Harness**: `test.py` verifies end-to-end agent functionality

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
DART_API_KEY=your_key_here
OPENAI_API_KEY=your_openai_key_here
```

### 4. Run the System
``` bash
python main.py
```

### Run Test
``` bash
python test.py
```

### Dependencies
``` cpp
pandas>=1.3.0
yfinance>=0.2.30
requests>=2.25.0
python-dotenv>=0.20.0
pyyaml>=6.0
cerberus>=1.3.4
python-dateutil>=2.8.2
kafka-python>=2.0.2
asyncio-mqtt>=0.16.1
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
