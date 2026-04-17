# 🏦 Crypto Intelligence System V10.0-r1

**Professional cryptocurrency market prediction system with calibrated uncertainty and self-correction**

[![Progress](https://img.shields.io/badge/Progress-13.3%25-blue.svg)](./MARKET_MIND/CONFIG/component_status.json)
[![Components](https://img.shields.io/badge/Components-4%2F30-green.svg)](#components-status)
[![Architecture](https://img.shields.io/badge/Architecture-8--layer-orange.svg)](#architecture)

## 🎯 Overview

CIS V10.0-r1 is a sophisticated Research Operating System for cryptocurrency markets featuring:

- **🔮 Calibrated Uncertainty** - Honest confidence assessment
- **🔄 Self-Correction** - Learns from prediction outcomes
- **⚡ Fast Lane** - Sub-200ms critical operations
- **🏗️ 8-Layer Architecture** - Modular and scalable design
- **🤖 Financial CTO** - Autonomous task management

## 📊 Current Status

**Ready Components (4/30):**
- ✅ `initialize_system` - Core system initialization
- ✅ `schema_layer` - JSON validation (6 schemas)
- ✅ `data_quality_gates` - Quality checks with failover
- ✅ `context_orchestrator` - Input assembly with parallel execution

**Progress:** 13.3% complete | **Next:** UI and research components

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│            CIS V10.0-r1                 │
├─────────────────────────────────────────┤
│ H │ INTERFACE & OPS    │ UI, API, Logs  │
│ G │ NEWS & TRUST       │ News, Sources  │
│ F │ FEEDBACK & CONTROL │ PI-lite, Brake │
│ E │ VALIDATION         │ Backtest, OOS  │
│ D │ MODEL CORE         │ ML, Aggregation│
│ C │ KNOWLEDGE & CTX    │ KB, Context    │
│ B │ DATA & FEATURES    │ Store, Quality │
│ A │ RESEARCH CORE      │ Experiments    │
└─────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 22+ (for MCP integration)
- Git

### Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/crypto-intelligence-system-v10.git
cd crypto-intelligence-system-v10

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies (for MCP)
npm install

# Check system status
python cis-cli.py status
```

### Usage

```bash
# System status
python cis-cli.py status

# View dashboard (opens in browser)
python dashboard.py

# Next task to work on
python cis-cli.py next

# Execute next task
python ENGINE/task_executor.py
```

## 📁 Project Structure

```
MARKET_MIND/                 # Core CIS V10.0-r1 system
├── ENGINE/                  # Execution modules
├── SCHEMAS/                 # JSON validation schemas  
├── CONFIG/                  # Configuration files
├── LAYER_A_RESEARCH/        # Research and experiments
├── LAYER_B_DATA/            # Data and feature store
├── LAYER_C_KNOWLEDGE/       # Knowledge base
├── LAYER_D_MODEL/           # ML models and predictions
├── LAYER_E_VALIDATION/      # Backtesting and validation
├── LAYER_F_FEEDBACK/        # Feedback and control
├── LAYER_G_NEWS/            # News analysis
└── LAYER_H_INTERFACE/       # APIs and logs

TASKS/                       # Task management
├── ACTIVE/                  # Current tasks
├── COMPLETED/               # Finished tasks
└── TEMPLATES/               # Task templates
```

## 🔧 Configuration

Key configuration files:
- [`component_status.json`](./MARKET_MIND/CONFIG/component_status.json) - Component readiness
- [`system_manifest.json`](./MARKET_MIND/CONFIG/system_manifest.json) - System version info
- [`market_axioms.json`](./MARKET_MIND/CONFIG/market_axioms.json) - Market assumptions

## 🧪 Components Status

| Component | Status | Notes |
|-----------|--------|-------|
| initialize_system | ✅ Ready | System initialization |
| schema_layer | ✅ Ready | 6 schemas + validator |
| data_quality_gates | ✅ Ready | 6 gates, stale cache fallback |
| context_orchestrator | ✅ Ready | 6 inputs, parallel AXM+Prior |
| streamlit_ui_basic | ⏳ Pending | Web interface |
| hypothesis_formalizer | ⏳ Pending | Research formalization |
| ... | ⏳ Pending | 26 more components |

Full status: [component_status.json](./MARKET_MIND/CONFIG/component_status.json)

## 📖 Documentation

- **[System Architecture](./CRYPTO_INTELLIGENCE_SYSTEM_STRUCTURE.md)** - Complete architectural overview
- **[Project Description](./PROJECT_DESCRIPTION.md)** - Detailed project documentation  
- **[Technical Specification](./TZ/)** - Technical requirements V10.0-r1
- **[Interface Guide](./INTERFACES_GUIDE.md)** - UI and API documentation
- **[Quick Start Guide](./QUICKSTART.md)** - Getting started guide

## 🔬 Research & Development

The system implements advanced financial ML concepts:

- **Two-Transaction Model** - Forecast/Feedback separation
- **Conformal UQ** - Uncertainty quantification
- **6 Operating Modes** - Normal/Degraded/Brake/Recovery/Stale
- **Shock Score System** - Market anomaly detection
- **Pattern Decay Monitoring** - Model degradation tracking

## 🤝 Contributing

1. Check [active tasks](./TASKS/ACTIVE/)
2. Review [task template](./TASKS/TEMPLATES/task_template.md)
3. Execute via `python ENGINE/task_executor.py`
4. Submit PR with completed deliverables

## ⚠️ Disclaimer

This system is for **educational and research purposes only**. It is NOT financial advice. 
Cryptocurrency trading involves high risk and you may lose your entire investment.

## 📄 License

MIT License - see [LICENSE](./LICENSE) for details.

---

**Version:** V10.0-r1  
**Status:** 4/30 components ready (13.3%)  
**Last Updated:** April 2026

*Built with Claude Sonnet 4 and Financial CTO automation*