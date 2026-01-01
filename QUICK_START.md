# ⚡ Quick Start Guide

## 🎯 Fastest Way to Run

### Option 1: Backtesting (Recommended for First Time)

**Double-click:** `setup.bat` (installs everything)  
**Then double-click:** `run_backtest.bat` (runs backtest)

### Option 2: Live Trading (Requires MT5)

1. **Open MetaTrader 5** and login to a **DEMO account**
2. **Add XAUUSD** to Market Watch
3. **Enable Algo Trading** (button in toolbar)
4. **Double-click:** `run_live.bat`

---

## 📋 Manual Setup (If batch files don't work)

### 1. Install Dependencies
```bash
cd "nur_phase1 updated/nur_phase1 (copy 1)"
pip install -r requirements.txt
```

### 2. Run Backtest
```bash
python backtest/engine_simple.py
```

### 3. Run Live Trading
```bash
python main.py
```

---

## ✅ What You Need

- ✅ Python 3.8+ installed
- ✅ For backtesting: Nothing else needed!
- ✅ For live trading: MT5 terminal running

---

## 🚨 Important

- **Always use a DEMO account** for testing
- **Backtesting doesn't need MT5** - perfect for first-time testing
- **Live trading requires MT5** to be running

---

## 📖 Full Documentation

See `SETUP_GUIDE.md` for detailed instructions.

