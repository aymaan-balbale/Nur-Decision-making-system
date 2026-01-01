# 🚀 Nur Trading Agent - Setup & Run Guide

## Prerequisites

1. **Python 3.8+** installed
2. **MetaTrader 5** installed (for live trading only)
3. **XAUUSD (Gold)** symbol available in MT5 Market Watch

---

## 📦 Step 1: Install Dependencies

### Option A: Using pip (Recommended)

```bash
cd "nur_phase1 updated/nur_phase1 (copy 1)"
pip install -r requirements.txt
pip install MetaTrader5
```

### Option B: Manual Installation

```bash
pip install pandas>=2.0.0
pip install numpy>=1.24.0
pip install python-dateutil>=2.8.2
pip install MetaTrader5
```

---

## 🧪 Step 2: Run Backtesting (No MT5 Required)

Backtesting allows you to test the strategy on historical data without needing MT5.

### Quick Backtest

```bash
cd "nur_phase1 updated/nur_phase1 (copy 1)"
python backtest/engine_simple.py
```

### Full Backtest

```bash
python backtest/engine.py
```

### Custom Backtest

```bash
python run_simple_backtest.py
```

**Note:** Make sure you have historical data at:
- `data/historical_xauusd_m1.csv`

If you don't have data, you can:
1. Export from MT5 (History Center → XAUUSD M1 → Export)
2. Or use the data generator: `python data/generate_mt5_data.py`

---

## 🔴 Step 3: Run Live Trading (MT5 Required)

### Prerequisites for Live Trading:

1. **MT5 Terminal** must be running
2. **XAUUSD** must be in Market Watch
3. **Algo Trading** must be enabled in MT5
4. **Expert Advisor (EA)** must be attached to XAUUSD chart (if using file-based bridge)

### Option A: Using Python MT5 API (Recommended)

```bash
cd "nur_phase1 updated/nur_phase1 (copy 1)"
python main.py
```

This will:
- Connect to MT5 automatically
- Monitor live price ticks
- Calculate EMA200 in real-time
- Generate BUY/SELL signals
- Send trade commands to MT5

### Option B: Using File-Based Bridge

If you're using the file-based bridge (older method):

1. **Start MT5 EA** on XAUUSD M1 chart
2. **Run Python script:**

```bash
python ema200.py
```

---

## 📊 Step 4: Monitor & Test

### View Market Data

```bash
python read_market.py
```

### Test Strategy Logic

```bash
python core/strategy.py
```

### Test Risk Manager

```bash
python core/risk_manager.py
```

### Test Learning System

```bash
python core/learner.py
```

---

## ⚙️ Configuration

### MT5 Connection Settings

The system automatically connects to MT5. If you need to change settings, edit:
- `bridge/bridge.py` - MT5 connection and file paths

### Trading Parameters

Edit `main.py` to change:
- Stop Loss: `sl = round(price - 2.0, 2)` (line 101)
- Take Profit: `tp = round(price + 4.0, 2)` (line 102)

### Backtest Settings

Edit `backtest/engine.py` to change:
- Initial balance
- Risk per trade
- Risk-reward ratio
- Commission and spread

---

## 🐛 Troubleshooting

### "MetaTrader5 not found"
```bash
pip install MetaTrader5
```

### "Symbol XAUUSD not found"
- Open MT5
- Add XAUUSD to Market Watch
- Right-click Market Watch → Show All

### "MT5 initialize failed"
- Make sure MT5 terminal is running
- Check if you're logged into a demo/live account
- Try restarting MT5

### "No data file found"
- Export data from MT5: History Center (F2) → XAUUSD → M1 → Export
- Save to: `data/historical_xauusd_m1.csv`

### "Permission denied" (Windows)
- Run PowerShell/CMD as Administrator
- Or check file permissions in MT5 Common Files folder

---

## 📁 Project Structure

```
nur_phase1 (copy 1)/
├── main.py              # 🚀 LIVE TRADING (Start here)
├── backtest/
│   ├── engine.py        # Full backtest engine
│   └── engine_simple.py # Simple backtest
├── bridge/
│   └── bridge.py        # MT5 connection
├── core/
│   ├── strategy.py      # Trading logic
│   ├── risk_manager.py  # SL/TP calculations
│   └── learner.py       # Q-learning system
└── data/
    └── historical_xauusd_m1.csv  # Historical data
```

---

## 🎯 Quick Start Commands

### For Backtesting (No MT5 needed):
```bash
cd "nur_phase1 updated/nur_phase1 (copy 1)"
python backtest/engine_simple.py
```

### For Live Trading (MT5 required):
```bash
cd "nur_phase1 updated/nur_phase1 (copy 1)"
python main.py
```

---

## ⚠️ Important Notes

1. **Demo Account Recommended**: Always test on a demo account first
2. **Risk Management**: The system uses fixed SL/TP in live mode. Adjust as needed.
3. **One Trade at a Time**: The system prevents overlapping trades
4. **Candle-Close Only**: Signals only trigger on candle close (no repainting)

---

## 📞 Need Help?

- Check logs in `logs/` directory
- Review error messages in console
- Verify MT5 connection: `python -c "import MetaTrader5 as mt5; print(mt5.initialize())"`

