# Nur-Decision-making-system

# System Architecture

## 1. Communication Bridge (`bridge/bridge.py`)
Connects Python to MetaTrader 5 using the official **MetaTrader5 Python API**.

**Functions**
- `read_market()`  
  Gets live tick data from MT5.
- `send_command()`  
  Sends trade orders (BUY/SELL) to MT5.
- `read_trade_exit()`  
  Monitors when trades close.

**Notes**
- Uses file-based IPC (`command.txt`, `trades.csv`) for reliability.

---

## 2. Core Trading Components

### Strategy (`core/strategy.py`, `core/ema_strategy.py`)
**EMA200 crossover logic**
- **BUY**
  - Price crosses above EMA200.
  - Previous candle was below or touching EMA200.
- **SELL**
  - Price crosses below EMA200.
  - Previous candle was above or touching EMA200.

**Rules**
- Candle-close only (no repainting).
- Includes early exit conditions:
  - Cross back
  - Stagnation
  - Max candle duration

---

### Risk Manager (`core/risk_manager.py`)
**Stop Loss**
- BUY: Previous candle low (with buffer).
- SELL: Previous candle high (with buffer).

**Take Profit**
- Risk–reward ratio (default **1.5:1**).
- Can use previous swing highs/lows if more optimal.

**Position Sizing**
- Based on account risk percentage.

---

### Market Data (`core/market.py`)
- Loads MT5-exported CSV files.
- Calculates EMA200 matching MT5’s method.
- Provides candle-by-candle data access.

---

### Learner (`core/learner.py`)
- Lightweight **Q-learning** (no deep learning).
- Learns from past trades to improve decisions.

**State Representation**
- Price distance to EMA
- Volatility
- Volume trend
- Overall market trend

**Actions**
- Enter
- Hold
- Exit (early/late)

**Rewards**
- `+1` → Take Profit  
- `-1` → Stop Loss  
- `-0.2` → Early exit loss  

**Constraints**
- Memory-efficient (compatible with 4GB RAM systems).

---

## Main Entry Points

### 1. Live Trading (`main.py`)
Real-time trading mode that:
- Connects to MT5.
- Monitors live price ticks.
- Calculates EMA200 in real time.
- Detects crossovers and sends trade commands.
- Tracks trade state (`WAITING → IN_TRADE → WAITING`).
- Monitors trade exits.

---

### 2. Backtesting (`backtest/engine.py`)
Simulates trading on historical data.

**Features**
- Candle-by-candle replay.
- Trade execution with SL/TP.
- Performance metrics:
  - Win rate
  - Profit factor
  - Drawdown
- Equity curve tracking.
- Daily trade limits and risk controls.

---

### 3. Standalone Scripts
- `ema200.py`  
  Simple EMA200 engine reading MT5 CSV files.
- `read_market.py`  
  Utility to monitor MT5 market data files.

---

## Trading Strategy Details

### Entry Conditions

**BUY**
- Current candle closes above EMA200.
- Previous candle closed below or touched EMA200.
- Not already in a trade.

**SELL**
- Current candle closes below EMA200.
- Previous candle closed above or touched EMA200.
- Not already in a trade.

---

### Risk Management
- Fixed SL/TP in live mode (demo values: `SL = 2.0`, `TP = 4.0`).
- Dynamic SL/TP in backtesting (based on previous candles and risk–reward).
- One trade at a time (no overlapping positions).
- Duplicate trade prevention.

---

MT5 Terminal
↓ Live Market Data (ticks)
Python Engine (main.py)
↓ EMA200 Calculation
↓ Crossover Detection
↓ Trade Command (BUY/SELL + SL/TP)
MT5 EA Executes Trade
↓ Trade Exit Monitoring
↓ State Reset → Ready for Next Trade



---

## Key Features
- Real-time MT5 integration.
- EMA200 crossover strategy.
- Risk management (SL/TP calculation).
- Historical backtesting.
- Learning component (Q-learning).
- File-based IPC for stability.
- No repainting (candle-close only).

---

## Project Structure

```text
Nur/
├── main.py                     # Live trading entry point
├── ema200.py                   # Standalone EMA engine
├── read_market.py              # Market data monitor
├── bridge/
│   └── bridge.py               # MT5 communication
├── core/
│   ├── strategy.py             # Trading strategy logic
│   ├── ema_strategy.py         # EMA-specific strategy
│   ├── risk_manager.py         # SL/TP calculations
│   ├── market.py               # Market data loader
│   ├── learner.py              # Q-learning system
│   ├── observer.py             # Trade monitoring
│   └── tracker.py              # Performance tracking
├── backtest/
│   ├── engine.py               # Main backtest engine
│   ├── engine_simple.py        # Simplified backtest
│   └── engine_fixed.py         # Fixed version
└── data/
    └── historical_xauusd_m1.csv # Historical data




Current Status

Live MT5 integration: Working

Strategy validation: Complete

Trade execution: Confirmed (test environment)

Backtesting: Functional

Learning system: Implemented (Q-learning)

Security: No secrets in repository

Disclaimer

This project is a prototype for learning and demonstration purposes.
It is not production-ready. The focus is on the EMA200 crossover strategy with basic risk management and a lightweight learning component that improves over time.
## Data Flow

