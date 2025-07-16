# Financial Multi-Agent System (MAS)

This repository contains a modular **multi-agent system** designed for financial market analysis and decision-making.  
Each agent is responsible for a distinct stage in the investment workflow — from data collection to signal generation — with communication managed through an orchestrator and shared event bus.

---

## Architecture Overview
financial_mas/
├── agents/ # Individual agents (market data, technical, screening, etc.)
│ ├── base_agent.py
│ ├── intent_agent.py
│ ├── market_data_agent.py
│ ├── orchestrator.py
│ ├── screening_agent.py
│ ├── signal_agent.py
│ └── technical_agent.py
├── config/ # Agent config, system settings, API keys
│ ├── agents.yaml
│ ├── api_keys.yaml
│ └── system_settings.yaml
├── core/ # Orchestrator, task scheduler, memory, communication
│ ├── communication.py
│ ├── memory_manager.py
│ ├── orchestrator.py
│ └── task_scheduler.py
├── messaging/ # Pub/Sub communication layer
│ ├── event_bus.py
│ └── pubsub_config.py
├── tools/ # External tools and APIs (e.g., HyperCLOVA)
│ ├── analysis_tools.py
│ ├── hyperclova_api.py
│ └── market_data_tools.py
├── utils/ # Logging, error handling, validation
│ ├── data_validator.py
│ ├── error_handler.py
│ └── logger.py
├── main.py # System entry point


---

##  Key Agents

| Agent Name           | Role                                                                 |
|----------------------|----------------------------------------------------------------------|
| `MarketDataAgent`    | Fetches real-time or historical market data                          |
| `TechnicalAgent`     | Performs technical indicator analysis (e.g., RSI, MACD)              |
| `ScreeningAgent`     | Filters assets based on configurable screening criteria              |
| `SignalAgent`        | Generates buy/sell/hold signals based on aggregated inputs           |
| `IntentAgent`        | Interprets user intent and routes tasks accordingly                  |
| `Orchestrator`       | Coordinates task execution, message flow, and memory updates         |

---

## ⚙ Configuration

All configs are located in the `config/` directory:

- `agents.yaml`: defines agent roles, names, and descriptions  
- `system_settings.yaml`: system-level parameters (e.g., threading, scheduling)  
- `api_keys.yaml`: API credentials for external tools and services

---

##  Getting Started

```bash
# (Optional) Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt  # (if you have one)

# Run the system
python main.py

---

##  License

This project is licensed under the MIT License.

---

## 🙋‍♀ Contact

Maintainer: [@annoeyed](https://github.com/annoeyed)  
For questions or collaboration inquiries, feel free to open an issue or pull request.

